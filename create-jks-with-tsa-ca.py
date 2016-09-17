import os
import random

from lxml import etree
from subprocess import call

import sys

TSA_CA_JKS = 'tsaCA.jks'

TEMP_PEM_FILENAME = 'tmp.pem'

TSA_SERVICE_TYPE_IDENTIFIERS = [
    'http://uri.etsi.org/TrstSvc/Svctype/TSA/TSS-QC',
    'http://uri.etsi.org/TrstSvc/Svctype/TSA/QTST',
    'http://uri.etsi.org/TrstSvc/Svctype/TSA/TSS-AdESQCandQES'
]

TSA_VALID_SERVICE_STATUSES = [
    'http://uri.etsi.org/TrstSvc/TrustedList/Svcstatus/granted',
    'http://uri.etsi.org/TrstSvc/TrustedList/Svcstatus/recognisedatnationallevel'
]

NS = {'ns': 'http://uri.etsi.org/02231/v2#', 'x': 'http://www.w3.org/XML/1998/namespace'}


def write_temp_pem_file(certificate):
    with open(TEMP_PEM_FILENAME, 'w') as tmp_file:
        tmp_file.write('-----BEGIN CERTIFICATE-----\n')
        tmp_file.write(certificate)
        tmp_file.write('\n-----END CERTIFICATE-----\n')


def generate_alias(service_provider_name):
    random_number = str(random.randint(1, 1000000000000))
    return service_provider_name + " [" + random_number + "]"


def check_valid_tsa_certificate(service_information):
    return service_information.find('ns:ServiceTypeIdentifier', NS).text in TSA_SERVICE_TYPE_IDENTIFIERS \
           and service_information.find('ns:ServiceStatus', NS).text in TSA_VALID_SERVICE_STATUSES


def add_certificate_to_keystore(alias):
    call(['keytool', '-import', '-storepass', 'changeit', '-noprompt', '-alias', alias, '-keystore', TSA_CA_JKS, '-file', 'tmp.pem'])
    os.remove(TEMP_PEM_FILENAME)


def get_service_provider_name(service_information):
    service_provider_name_element = service_information.xpath("../../../ns:TSPInformation/ns:TSPName/ns:Name[@x:lang='en']", namespaces=NS)[0]
    return service_provider_name_element.text if service_provider_name_element is not None else "certificate"


def main(path_to_xml):
    """
    Function get TSA certificates from xml file with TSL and add them to tsaCA.jks.
    If keystore tsaCA.jks doesn't exists it will be created.

    :arg path_to_xml: Path to xml file with TSL
    """
    if os.path.exists(path_to_xml):
        if os.path.exists(TSA_CA_JKS):
            print "Warning: file {0} exists. Certificates will be added to it.".format(TSA_CA_JKS)

        tree = etree.parse(path_to_xml)
        service_information_list = tree.findall('ns:TrustServiceProviderList/ns:TrustServiceProvider/ns:TSPServices/ns:TSPService/ns:ServiceInformation', NS)

        found_certificate_counter = 0
        for service_information in service_information_list:
            if check_valid_tsa_certificate(service_information):
                found_certificate_counter += 1
                x509_certificate_base64 = service_information.find('ns:ServiceDigitalIdentity/ns:DigitalId/ns:X509Certificate', NS).text
                write_temp_pem_file(x509_certificate_base64)
                service_provider_name = get_service_provider_name(service_information)
                add_certificate_to_keystore(generate_alias(service_provider_name))
        if found_certificate_counter == 0:
            print "There is no trusted TSA CA!"
        else:
            print "Added {0} certificates to keystore: {1}".format(found_certificate_counter, TSA_CA_JKS)
    else:
        print "XML file doesn't exists!"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print "Pass path to XML file with TSL"
        sys.exit(-1)
    sys.exit(0)