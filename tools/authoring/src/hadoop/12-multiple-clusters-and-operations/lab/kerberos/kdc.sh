# kdc.sh: a tiny MIT Kerberos KDC for the lab: realm LAB.MYPHATSHALA
set -e
apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq krb5-kdc krb5-admin-server > /dev/null
cp /lab/krb5.conf /etc/krb5.conf
mkdir -p /etc/krb5kdc /var/lib/krb5kdc
printf '[logging]\n kdc = STDERR\n[realms]\n LAB.MYPHATSHALA = {\n  database_name = /var/lib/krb5kdc/principal\n  acl_file = /etc/krb5kdc/kadm5.acl\n  key_stash_file = /etc/krb5kdc/stash\n }\n' > /etc/krb5kdc/kdc.conf
echo '*/admin@LAB.MYPHATSHALA *' > /etc/krb5kdc/kadm5.acl
kdb5_util create -s -r LAB.MYPHATSHALA -P masterkey123 > /dev/null
kadmin.local -q "addprinc -randkey nn/nn-secure@LAB.MYPHATSHALA" > /dev/null      # the NameNode service
kadmin.local -q "addprinc -randkey HTTP/nn-secure@LAB.MYPHATSHALA" > /dev/null    # its web UI (SPNEGO)
kadmin.local -q "addprinc -pw riya123 riya@LAB.MYPHATSHALA" > /dev/null           # two people
kadmin.local -q "addprinc -pw kabir123 kabir@LAB.MYPHATSHALA" > /dev/null
rm -f /keytabs/nn.keytab
kadmin.local -q "ktadd -k /keytabs/nn.keytab nn/nn-secure@LAB.MYPHATSHALA HTTP/nn-secure@LAB.MYPHATSHALA" > /dev/null
chmod 644 /keytabs/nn.keytab
kadmin.local -q "listprincs"
echo "KDC ready"
exec krb5kdc -n
