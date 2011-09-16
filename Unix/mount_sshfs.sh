#!/bin/sh
# install sshfs before

USER=username
VM=$USER@youhost.com

REMOTE_PATH=/home/$USER
LOCAL_PATH=~/src/


case $1 in
    connect)
        echo "connecting in $VM ..."
        ssh $VM
    ;;
    mountconnect)
        echo "mounting $VM:$REMOTE_PATH ..."
        sshfs -o idmap=user   $VM:$REMOTE_PATH $LOCAL_PATH
        echo "connecting in $VM ..."
        ssh $VM
    ;;
    mount)
        echo "mounting $VM:$REMOTE_PATH ..."
        sshfs -o idmap=user   $VM:$REMOTE_PATH $LOCAL_PATH
    ;;
esac
