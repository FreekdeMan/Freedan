from freedan.adwords_services.adwords import AdWords
from freedan.adwords_services.adwords import DEVICE_TO_ID


class AdGroup:
    """ Handling all AdGroup related functionality.
    AdGroups are the most integral part of AdWords since they contain Keywords, Ads and DeviceModifiers
    In our accounts AdGroups usually represent a route (in bus, train, flight and without vertical accounts)
    """
    def __init__(self, name):
        self.name = name

    def add_operation(self, campaign_id, max_cpc, status="ENABLED", adgroup_id=None, label_id=None):
        """ Operation to add a new adgroup """
        operation = {
            "xsi_type": "AdGroupOperation",
            "operator": "ADD",
            "operand": {
                "campaignId": campaign_id,
                "name": self.name,
                "status": status,
                "biddingStrategyConfiguration": {
                    "bids": [{
                        "xsi_type": "CpcBid",
                        "bid": {
                            "microAmount": max_cpc
                        }
                    }]
                }
            }
        }
        if adgroup_id is not None:
            operation["operand"]["id"] = adgroup_id

        if label_id is not None:
            operation["operand"]["labels"] = [{
                "id": label_id
            }]
        return operation

    @staticmethod
    def delete_operation(campaign_id, adgroup_id):
        """ Operation to delete an adgroup """
        operation = {
            "xsi_type": "AdGroupOperation",
            "operator": "SET",
            "operand": {
                "xsi_type": "AdGroup",
                "id": adgroup_id,
                "campaignId": campaign_id,
                "status": "REMOVED"
            }
        }
        return operation

    @staticmethod
    def set_name_operation(adgroup_id, new_name):
        """ Change name operation of campaign """
        operation = {
            "xsi_type": "AdGroupOperation",
            "operator": "SET",
            "operand": {
                "xsi_type": "AdGroup",
                "id": adgroup_id,
                "name": new_name
            }
        }
        return operation

    @staticmethod
    def set_device_modifier(adgroup_id, value, operator, device_type):
        """ Operation modify a device multiplier on an AdGroup """
        device_type = device_type.lower()
        device_type = "computers" if device_type == "desktop" else device_type

        operation = {
            "xsi_type": "AdGroupBidModifierOperation",
            "operator": operator,
            "operand": {
                "xsi_type": "AdGroupBidModifier",
                "adGroupId": adgroup_id,
                "criterion": {
                    "xsi_type": "Platform",
                    "id": DEVICE_TO_ID[device_type]
                },
                "bidModifier": value
            }
        }
        return operation

    @staticmethod
    def set_bid_operation(adgroup_id, max_cpc, convert_to_micro=True):
        """ Operation to change the bid of an AdGroup """
        if convert_to_micro:
            max_cpc = AdWords.euro_to_micro(max_cpc)

        operation = {
            "xsi_type": "AdGroupOperation",
            "operator": "SET",
            "operand": {
                "id": adgroup_id,
                "biddingStrategyConfiguration": {
                    "bids": [{
                        "xsi_type": "CpcBid",
                        "bid": {
                            "microAmount": max_cpc
                        }
                    }]
                }
            }
        }
        return operation

    def __repr__(self):
        """ user friendly representation of this AdGroup"""
        return self.name
