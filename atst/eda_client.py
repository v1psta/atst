class EDAClientBase(object):
    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        """
        Get a list of all contracts matching the given filters.
        """
        raise NotImplementedError()

    def get_contract(self, contract_number, status):
        """
        Get details for a contract.
        """
        raise NotImplementedError()


class MockEDAClient(EDAClientBase):
    def __init__(self, *args, **kwargs):
        pass

    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        return [
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
            {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
            },
        ]

    def get_contract(self, contract_number, status):
        if contract_number == "DCA10096D0052" and status == "y":
            return {
                "aco_mod": "01",
                "admin_dodaac": None,
                "cage_code": "1U305",
                "contract_no": "DCA10096D0052",
                "delivery_order": "0084",
                "duns_number": None,
                "issue_date": "20000228",
                "issue_dodaac": None,
                "location": "https://docsrv1.nit.disa.mil:443/eda/enforcer/C0414345.PDF?ver=1.4&loc=Y29udHJhY3RzL29nZGVuL3ZlbmRvci8xOTk4LzA5LzE0L0MwNDE0MzQ1LlBERg==&sourceurl=aHR0cHM6Ly9lZGE0Lm5pdC5kaXNhLm1pbC9wbHMvdXNlci9uZXdfYXBwLkdldF9Eb2M_cFRhYmxlX0lEPTImcFJlY29yZF9LZXk9OEE2ODExNjM2RUY5NkU2M0UwMzQwMDYwQjBCMjgyNkM=&uid=6CFC2B2322E86FD5E054002264936E3C&qid=19344159&signed=G&qdate=20180529194407GMT&token=6xQICrrrfIMciEJSpXmfsAYrToM=",
                "pay_dodaac": None,
                "pco_mod": "02",
                "amount": 2000000
            }
        else:
            return None


class EDAClient(EDAClientBase):
    def __init__(self, base_url, user_name, user_role):
        pass

    def list_contracts(
        self,
        contract_number=None,
        delivery_order=None,
        cage_code=None,
        duns_number=None,
    ):
        # TODO: Fetch the contracts CSV and transform them into dictionaries.
        # https://docs.python.org/3/library/csv.html#csv.DictReader
        raise NotImplementedError()

    def get_contract(self, contract_number, status):
        # TODO: Fetch the contract XML and transform it into a dictionary.
        # https://docs.python.org/3.7/library/xml.etree.elementtree.html
        raise NotImplementedError()



CONTRACT_XML = """
<ProcurementDocument>
<SchemaVersionUsed>2.5</SchemaVersionUsed>
<ProcurementInstrumentForm>DD 1155</ProcurementInstrumentForm>
<OriginatorDetails>
<InternalDocumentNumber>3244871</InternalDocumentNumber>
<DoDSystem>
<DITPRNumber>00000431</DITPRNumber>
<SystemAdministratorDoDAAC>704331</SystemAdministratorDoDAAC>
</DoDSystem>
</OriginatorDetails>
<AwardInstrument>
<ProcurementInstrumentHeader>
<ProcurementInstrumentIdentifier>
<ProcurementInstrumentOrigin>Department of Defense</ProcurementInstrumentOrigin>
<ProcurementInstrumentVehicle>Delivery Order</ProcurementInstrumentVehicle>
<NonDoDNumber>70433119F2644</NonDoDNumber>
<ProcurementInstrumentDescription>Represented Contract</ProcurementInstrumentDescription>
</ProcurementInstrumentIdentifier>
<ProcurementInstrumentIdentifier>
<ProcurementInstrumentOrigin>Department of Defense</ProcurementInstrumentOrigin>
<ProcurementInstrumentVehicle>Basic Ordering Agreement</ProcurementInstrumentVehicle>
<NonDoDNumber>W81K0419G0001</NonDoDNumber>
<ProcurementInstrumentDescription>Ordering Instrument</ProcurementInstrumentDescription>
</ProcurementInstrumentIdentifier>
<BasicInformation>
<ContingencyContract>false</ContingencyContract>
<DocumentPurpose>Original</DocumentPurpose>
<EmergencyRequestContract>false</EmergencyRequestContract>
<PricingArrangement>
<PricingArrangementBase>Firm Fixed Price</PricingArrangementBase>
</PricingArrangement>
</BasicInformation>
<ClauseInformation>
<RegulationURL>
http://farsite.hill.af.mil/reghtml/regs/far2afmcfars/fardfars/far/52_220.htm#P810_149596
</RegulationURL>
<ClauseDetails>
<RegulationOrSupplement>FAR</RegulationOrSupplement>
<ClauseNumber>52.222-50</ClauseNumber>
<ClauseTitle>Combating Trafficking in Persons.</ClauseTitle>
<ClauseEffectiveDate>2015-05</ClauseEffectiveDate>
<ClauseText>
<ClauseFullText>
    [ lots of text ]
</ClauseFullText>
</ClauseText>
<Section>I</Section>
</ClauseDetails>
<ClauseDetails>
<RegulationOrSupplement>FAR</RegulationOrSupplement>
<ClauseNumber>52.245-1</ClauseNumber>
<ClauseTitle>Government Property.</ClauseTitle>
<ClauseEffectiveDate>2012-04</ClauseEffectiveDate>
<ClauseText>
<ClauseFullText>
    [ lots of text ]
</ClauseFullText>
</ClauseText>
<Section>I</Section>
</ClauseDetails>
</ClauseInformation>
<ProcurementInstrumentDates>
<ProcurementInstrumentEffectiveDate>2016-02-04</ProcurementInstrumentEffectiveDate>
<ContractingOfficer>
<SignatureDate>2016-01-25</SignatureDate>
<SigneeDetails>
<Name>DALE WOLFE</Name>
<ContactMethod>
<MethodDescription>Telephone</MethodDescription>
<MethodValue>520-533-9132</MethodValue>
</ContactMethod>
</SigneeDetails>
</ContractingOfficer>
</ProcurementInstrumentDates>
<ProcurementInstrumentAddresses>
<AddressDescription>Contractor</AddressDescription>
<Address>
<OrganizationID>
<Cage>0Z7K0</Cage>
<DunsNumber>808152482</DunsNumber>
</OrganizationID>
<OrganizationNameAddress>
<OrganizationName>CACI TECHNOLOGIES, INC</OrganizationName>
<OrganizationAddress>
<FreeFormAddress>
<AddressLine1>6933 Gateway Ct</AddressLine1>
<AddressLine2>Manassas VA, 20109</AddressLine2>
</FreeFormAddress>
</OrganizationAddress>
</OrganizationNameAddress>
</Address>
</ProcurementInstrumentAddresses>
<ProcurementInstrumentAddresses>
<AddressDescription>Contract Issuing Office</AddressDescription>
<Address>
<OrganizationID>
<DoDAAC>704331</DoDAAC>
</OrganizationID>
<OrganizationNameAddress>
<OrganizationName>FEMA DISTRIBUTION CENTER</OrganizationName>
<OrganizationAddress>
<FreeFormAddress>
<AddressLine1>3870 S. SIDE INDUSTRIAL CTR</AddressLine1>
<AddressLine2>ATLANTA GA, 30354</AddressLine2>
</FreeFormAddress>
</OrganizationAddress>
</OrganizationNameAddress>
</Address>
<Contact>
<Name>GENE BARBER</Name>
<ContactMethod>
<MethodDescription>Telephone</MethodDescription>
<MethodValue>(202) 646-2727</MethodValue>
</ContactMethod>
</Contact>
</ProcurementInstrumentAddresses>
<ProcurementInstrumentAddresses>
<AddressDescription>Contract Administrative Office</AddressDescription>
<Address>
<OrganizationID>
<DoDAAC>704331</DoDAAC>
</OrganizationID>
<OrganizationNameAddress>
<OrganizationName>FEMA DISTRIBUTION CENTER</OrganizationName>
<OrganizationAddress>
<FreeFormAddress>
<AddressLine1>3870 S. SIDE INDUSTRIAL CTR</AddressLine1>
<AddressLine2>ATLANTA GA, 30354</AddressLine2>
</FreeFormAddress>
</OrganizationAddress>
</OrganizationNameAddress>
</Address>
</ProcurementInstrumentAddresses>
<ProcurementInstrumentAddresses>
<AddressDescription>Paying Office</AddressDescription>
<Address>
<OrganizationID>
<DoDAAC>HQ0131</DoDAAC>
</OrganizationID>
<OrganizationNameAddress>
<OrganizationName>DEFENSE FINANCE AND ACCOUNTING SVC</OrganizationName>
<OrganizationAddress>
<FreeFormAddress>
<AddressLine1>P.O. BOX 369016</AddressLine1>
<AddressLine2>COLUMBUS OH, 43236</AddressLine2>
</FreeFormAddress>
</OrganizationAddress>
</OrganizationNameAddress>
</Address>
</ProcurementInstrumentAddresses>
<ProcurementInstrumentAddresses>
<AddressDescription>Ship To</AddressDescription>
<Address>
<OrganizationID>
<DoDAAC>S0302A</DoDAAC>
</OrganizationID>
<OrganizationNameAddress>
<OrganizationName>DCMA PHOENIX</OrganizationName>
<OrganizationAddress>
<FreeFormAddress>
<AddressLine1>40 NORTH CENTRAL AVE, STE 400</AddressLine1>
<AddressLine2>TWO RENAISSANCE SQUARE</AddressLine2>
<AddressLine3>PHOENIX AZ, 85004</AddressLine3>
</FreeFormAddress>
</OrganizationAddress>
</OrganizationNameAddress>
</Address>
</ProcurementInstrumentAddresses>
<ProcurementInstrumentAmounts>
<OtherAmounts>
<AmountDescription>Header Only - Total Contract Value</AmountDescription>
<Amount>192000.00</Amount>
</OtherAmounts>
</ProcurementInstrumentAmounts>
<DeliveryDetails>
<DeliveryDates>
<DeliveryDescription>Delivery Requested By</DeliveryDescription>
<DeliveryDate>
<DateElement>2016-01-16</DateElement>
</DeliveryDate>
</DeliveryDates>
</DeliveryDetails>
<ReferenceNumber>
<ReferenceDescription>
Defense Priorities Allocation System (DPAS) Priority Rating
</ReferenceDescription>
<ReferenceValue>DO-A7</ReferenceValue>
<Section>A</Section>
</ReferenceNumber>
<Shipping>
<FoBDetails>
<PaymentMethod>Contractor</PaymentMethod>
<FoBPoint>Origin (after Loading)</FoBPoint>
</FoBDetails>
</Shipping>
</ProcurementInstrumentHeader>
<ContractLineItems>
<LineItems>
<LineItemIdentifier>
<DFARS>
<LineItem>
<LineItemType>CLIN</LineItemType>
<LineItemBase>0001</LineItemBase>
</LineItem>
</DFARS>
</LineItemIdentifier>
<LineItemBasicInformation>
<OptionLineItem>false</OptionLineItem>
<PricingArrangement>
<PricingArrangementBase>Cost No Fee</PricingArrangementBase>
</PricingArrangement>
<ProductServicesOrdered>
<ProductOrService>Real Property</ProductOrService>
<ProductServiceDescription>Radio Dishes</ProductServiceDescription>
<Quantity>3</Quantity>
<ItemUIDRequired>false</ItemUIDRequired>
<PriceBasis>Estimated</PriceBasis>
<UnitOfMeasure>Each</UnitOfMeasure>
<UnitPrice>64000.00</UnitPrice>
<ProductServiceData>
<DataDescription>Manufacturer's Part Number</DataDescription>
<DataValue>5L33M7730291DX081</DataValue>
</ProductServiceData>
</ProductServicesOrdered>
</LineItemBasicInformation>
<LineItemAmounts>
<ItemOtherAmounts>
<AmountDescription>Estimated Cost</AmountDescription>
<Amount>192000.00</Amount>
</ItemOtherAmounts>
<ItemOtherAmounts>
<AmountDescription>Not to Exceed Amount (Funding)</AmountDescription>
<Amount>200000.00</Amount>
</ItemOtherAmounts>
</LineItemAmounts>
</LineItems>
</ContractLineItems>
</AwardInstrument>
</ProcurementDocument>
"""
