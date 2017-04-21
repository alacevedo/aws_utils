#!/bin/bash

# Realiza el snapshot del EBS de datos de las instancias de ops
# Requiere de los siguientes prerequisitos:
#	- aws cli configurado
#	- jq

_fechaini=`date +%Y%m%d%H%M`
#Se detienen los servicios para detener el i/o sobre el filesystem
echo "Fecha-hora inicio: "$_fechaini
echo "Deteniendo servicios"

sudo service apache2 stop
if [ $? -eq 0 ]; then
    echo "Apache stop exitoso"
    sudo service mysql stop
    if [ $? -eq 0 ]; then
        echo "Mysql stop exitoso"
    else
        echo "Mysql stop error" >&2  
        exit $?
    fi
else
    echo "Apache stop error" >&2
    exit $?
fi

#desmontando particion para realizar snapshot
#Notar que la partición asume que está en /dev/xvdb
sudo umount /dev/xvdb
if [ $? -eq 0 ]; then
    echo "/dev/xvdb desmontado"
else
    echo "Error un umont /dev/xvdb" >&2
    exit $?
fi

# Obtiene los identificadores de las instancias con el tag "ops"
# luego identifica los volumenes con el tag "data" y crea el snapshot
_instancias=`aws ec2 describe-instances --filters "Name=tag-value, Values=ops" | jq -r ".Reservations[].Instances[].InstanceId"`
echo "Se inicia toma de snapshots"
for instancia in $_instancias; do
    echo "Comenzando backup instancia: " $instancia
	_volumes=`aws ec2 describe-volumes --filters "Name=attachment.instance-id,Values=$instancia" "Name=tag-value,Values=data" | jq -r .Volumes[].VolumeId`
	for volume in $_volumes; do
	    echo "Comenzando backup volumen: " $volume
        _fecha=`date +%Y%m%d`     
        _snapshot=`aws ec2 create-snapshot --volume-id $volume --description "$_fecha" | jq -r .SnapshotId`
        _status=`aws ec2 describe-snapshots --snapshot-id $_snapshot | jq -r .Snapshots[].State`
        while [ $_status != 'completed' ]; do
            _status=`aws ec2 describe-snapshots --snapshot-id $_snapshot | jq -r .Snapshots[].State`
   	        echo "Esperando 2 segundos"
    	    echo "Snapshot en estado: " $_status
	        sleep 2
        done        
	done
done

#montando particiones
sudo mount -a
if [ $? -eq 0 ]; then
    echo "Remontando todas las particiones"
else
    echo "Error al montar particiones" >&2
    exit $?
fi

#se vuelven a iniciar los servicios
echo "Se vuelven a iniciar los servicios"
sudo service mysql start
if [ $? -eq 0 ]; then
    echo "Mysql start exitoso"
    sudo service apache2 start
    if [ $? -eq 0 ]; then
        echo "Apache start exitoso"
    else
        echo "Apache start error" >&2
        exit $?
    fi
else
    echo "Mysql start error" >&2
    exit $?
fi

_fechafin=`date +%Y%m%d%H%M`
echo "Fecha-hora fin: "$_fechafin
