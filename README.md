# Scripts for handling XML file with TSL list

Script working on XML file with TSL (Trusted Service List) - technical specification provided by Electronic Signatures and Infrastructures (ESI).
Polish TSL is available on site: https://www.nccert.pl/tsl.htm
Script should work with other national trusted service lists.

Requirements:

- python 2.7
- keytool (http://docs.oracle.com/javase/6/docs/technotes/tools/solaris/keytool.html)

## Generate JKS with TSA certificates

If you need keystore with TSA CA you can run
```python create-jks-with-tsa-ca.py [XML_FILE]```

It generates "tsaCA.jks" file with TSA certificates.
If file "tsaCA.jks" exists script will add certificates to it.
Password to JKS is ```changeit```. 
Alias of added certificates is name of trusted service provider plus random number to avoid alias conflicts.

