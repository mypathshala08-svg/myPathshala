# kerberos_lab.sh: the same commands on an unsecured cluster and on a Kerberos-secured NameNode.
# Run on your PC: part 1 uses the Module 8 lab, part 2 the lab12k containers.
echo "######## 1. UNSECURED (Module 8 lab): Hadoop believes whatever user name you claim"
docker exec lab8-namenode-1 bash -c '
hdfs dfs -mkdir -p /secure_demo && hdfs dfs -chmod 700 /secure_demo && hdfs dfs -put -f /etc/hostname /secure_demo/salaries.csv
echo "-- as riya (not the owner):"
HADOOP_USER_NAME=riya hdfs dfs -cat /secure_demo/salaries.csv 2>&1 | grep -o "Permission denied.*" | cut -c1-120
echo "-- as riya, claiming to be the owner \"hadoop\":"
HADOOP_USER_NAME=hadoop hdfs dfs -ls /secure_demo 2>&1 | grep salaries | awk "{print \$1, \$3, \$8}"
echo "-- as anyone, claiming to be the owner, deleting it:"
HADOOP_USER_NAME=hadoop hdfs dfs -rm -r -skipTrash /secure_demo 2>&1 | grep -v INFO'
echo
echo "######## 2. KERBEROS (lab12k): identity comes from a ticket, not from a variable"
docker exec lab12k-client-1 bash -c 'quiet() { grep -vE "^\s|^Usage|^$|^Generic|^command|^-[a-z]+ <|WARN"; }

echo "-- no ticket:"
hdfs dfs -ls / 2>&1 | grep -oE "Client cannot authenticate via:\[[A-Z, ]+\]|AccessControlException|GSS initiate failed" | sort -u | head -2
echo "-- claiming a name does nothing now:"
HADOOP_USER_NAME=nn hdfs dfs -ls / 2>&1 | grep -oE "Client cannot authenticate via:\[[A-Z, ]+\]" | head -1
echo "-- the service admin logs in with its keytab and makes a home folder for riya:"
kinit -kt /keytabs/nn.keytab nn/nn-secure@LAB.MYPHATSHALA
hdfs dfs -mkdir -p /user/riya /payroll 2>&1 | quiet
hdfs dfs -chown riya /user/riya; hdfs dfs -chmod 700 /payroll
hdfs dfs -touchz /payroll/salaries.csv      # our secure lab has no DataNode, so we create empty files (metadata only)
kdestroy
echo "-- riya logs in with her password:"
echo riya123 | kinit riya@LAB.MYPHATSHALA > /dev/null
klist | sed -n "1,6p"
hdfs dfs -touchz /user/riya/notes.txt
hdfs dfs -ls /user/riya | grep notes | awk "{print \$1, \$3, \$8}"
echo "-- riya tries the payroll folder, and tries to pretend:"
hdfs dfs -cat /payroll/salaries.csv 2>&1 | grep -o "Permission denied.*" | cut -c1-110
HADOOP_USER_NAME=nn hdfs dfs -cat /payroll/salaries.csv 2>&1 | grep -o "Permission denied.*" | cut -c1-110
echo "-- the cache holds only the TGT; Java asks the KDC for the NameNode service ticket in memory"
klist | grep -E "krbtgt|nn/"
echo "-- wrong password:"
kdestroy; echo wrongpass | kinit riya@LAB.MYPHATSHALA 2>&1 | tail -1'
echo "-- the KDC log saw all of it:"
docker logs lab12k-kdc-1 2>&1 | grep -E "AS_REQ|TGS_REQ" | sed -E 's/^.*krb5kdc\[[0-9]+\]\(info\): //; s/ \([0-9]+ etypes \{[^}]*\}\)//; s/authtime [0-9]+, etypes \{[^}]*\}, //' | uniq -c | tail -8
echo
echo "######## 3. AUTHORIZATION beyond owner/group: an HDFS ACL (Module 8 lab; the idea Ranger extends)"
docker exec lab8-namenode-1 bash -c '
hdfs dfs -mkdir -p /finance && hdfs dfs -chmod 750 /finance && hdfs dfs -touchz /finance/q3.csv
hdfs dfs -setfacl -m user:kabir:r-x /finance
hdfs dfs -getfacl /finance
echo "-- kabir (named in the ACL): $(HADOOP_USER_NAME=kabir hdfs dfs -ls /finance 2>&1 | grep -c q3.csv) file visible"
echo "-- riya (not in the ACL): $(HADOOP_USER_NAME=riya hdfs dfs -ls /finance 2>&1 | grep -o "Permission denied: user=riya" )"
hdfs dfs -ls -d /finance | awk "{print \$1, \$3, \$8}"
hdfs dfs -rm -r -skipTrash /finance > /dev/null'
