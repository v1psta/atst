Right now, we have two client certificates:

- atat.mil.crt: beautiful, good, works great
- bad-atat.mil.crt: banned, very bad, is on the CRL

I more or less used [this article](https://access.redhat.com/documentation/en-us/red_hat_update_infrastructure/2.1/html/administration_guide/chap-red_hat_update_infrastructure-administration_guide-certification_revocation_list_crl) to generate the CRL. Note that I departed from it slightly and used a variation on the openssl config recommended by the ca man page (`man ca`).

I added the new crl:

```
openssl crl -inform pem -in ssl/client-certs/client-ca.crl -outform der -out crl/simon.crl
```

Running the scripts verifies that the good one is good and the bad one is bad.

We can also verify with OpenSSL. First concatenate the CA Bundle and the CRL:

```
cat ssl/server-certs/ca-chain.pem ssl/client-certs/client-ca.crl > /tmp/test.pem
```

Verify the certs:

```
openssl verify -verbose -CAfile /tmp/test.pem -crl_check ssl/client-certs/bad-atat.mil.crt
> error 23 at 0 depth lookup:certificate revoked
openssl verify -verbose -CAfile /tmp/test.pem -crl_check ssl/client-certs/atat.mil.crt
> atat.mil.crt: OK
```

