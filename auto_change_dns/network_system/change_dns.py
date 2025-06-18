from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import (
    UpdateDomainRecordRequest,
)
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import (
    AddDomainRecordRequest,
)
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import (
    DescribeDomainRecordsRequest,
)


class AliyunDNSUpdater:
    """
    Module for updating DNS records on Alibaba Cloud via RAM credentials.
    """

    def __init__(
        self, access_key_id: str, access_key_secret: str, region: str = "cn-hangzhou"
    ):
        """
        Initialize the AcsClient with RAM credentials.
        """
        self.client = AcsClient(access_key_id, access_key_secret, region)

    def get_record_id(self, domain: str, rr: str, record_type: str = "A"):
        """
        Retrieve the record ID for a given domain and RR.
        """
        request = DescribeDomainRecordsRequest()
        request.set_DomainName(domain)
        request.set_KeyWord(rr)
        request.set_PageSize(50)
        response = self.client.do_action_with_exception(request)
        # Parse JSON and find matching RR and type
        import json

        data = json.loads(response)
        for record in data.get("DomainRecords", {}).get("Record", []):
            if record.get("RR") == rr and record.get("Type") == record_type:
                return record.get("RecordId")
        return None

    def update_record(
        self, record_id: str, rr: str, record_type: str, value: str, ttl: int = 600
    ):
        """
        Update an existing DNS record.
        """
        request = UpdateDomainRecordRequest()
        request.set_RecordId(record_id)
        request.set_RR(rr)
        request.set_Type(record_type)
        request.set_Value(value)
        request.set_TTL(ttl)
        return self.client.do_action_with_exception(request)

    def add_record(
        self, domain: str, rr: str, record_type: str, value: str, ttl: int = 600
    ):
        """
        Add a new DNS record.
        """
        request = AddDomainRecordRequest()
        request.set_DomainName(domain)
        request.set_RR(rr)
        request.set_Type(record_type)
        request.set_Value(value)
        request.set_TTL(ttl)
        return self.client.do_action_with_exception(request)

    def set_dns(
        self, domain: str, rr: str, record_type: str, value: str, ttl: int = 600
    ):
        """
        Create or update DNS record as needed.
        """
        record_id = self.get_record_id(domain, rr, record_type)
        if record_id:
            return self.update_record(record_id, rr, record_type, value, ttl)
        else:
            return self.add_record(domain, rr, record_type, value, ttl)


# Example usage:
# updater = AliyunDNSUpdater("yourAccessKeyId", "yourAccessKeySecret")
# response = updater.set_dns("example.com", "subdomain", "A", "1.2.3.4")
# print(response)
