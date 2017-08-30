import pytest
from tests import service_suds_client


def init_native_adwords_account_label(name, label_id):
    suds_client = service_suds_client("ManagedCustomerService")
    label = suds_client.factory.create("AccountLabel")
    label.name = name
    label.id = label_id
    return label


def init_native_adwords_account():
    suds_client = service_suds_client("ManagedCustomerService")

    # create ad_account
    ad_account = suds_client.factory.create("ManagedCustomer")
    ad_account.name = "Test1"
    ad_account.customerId = "302-203-1203"
    ad_account.currencyCode = "CAD"
    ad_account.dateTimeZone = "America/Vancouver"
    ad_account.canManageClients = False
    ad_account.testAccount = False
    ad_account.accountLabels = [
        init_native_adwords_account_label("test1", 0),
        init_native_adwords_account_label("this_is_a_label", 1)
    ]
    return ad_account


def test_account_label():
    from freedan import AccountLabel

    adwords_label = init_native_adwords_account_label("test_acc_label", 90)
    acc_label = AccountLabel.from_adwords_account_label(adwords_label)
    assert acc_label.name == "test_acc_label"
    assert acc_label.id == 90


def test_account():
    from freedan import Account, AccountLabel

    # test initiation from native adwords account
    adwords_account = init_native_adwords_account()
    account = Account.from_ad_account(ad_account=adwords_account)
    assert account.name == "Test1"
    assert account.id == "302-203-1203"
    assert account.currency == "CAD"
    assert account.time_zone == "America/Vancouver"
    assert not account.is_mcc
    assert not account.is_test

    # check labels
    assert all(isinstance(e, AccountLabel) for e in account.labels)
    label1, label2 = account.labels
    assert (label1.name, label1.id) == ("test1", 0)
    assert (label2.name, label2.id) == ("this_is_a_label", 1)

    # test initiation from name
    account = Account.from_name("Test2")
    assert account.name == "Test2"
    assert account.id is None
    assert account.currency is None
    assert account.time_zone is None
    assert account.is_mcc is None
    assert account.is_test is None
    assert account.labels is None


def test_budget():
    from freedan import CampaignBudget
    from freedan.adwords_services.adwords_service import MICRO_FACTOR

    budget = CampaignBudget(amount=200)
    assert budget.amount == 200
    assert budget.micro_amount == 200 * MICRO_FACTOR


def test_add_budget(capfd):
    from tests import adwords_service, no_error_stdout
    from freedan import CampaignBudget

    budget = CampaignBudget(amount=200)
    operations = [budget.add_operation(temp_id=-1)]

    adwords_service.upload(operations, is_debug=True)

    out, err = capfd.readouterr()
    assert out == no_error_stdout


def test_eta():
    from freedan import ExtendedTextAd

    # good eta with some conversions
    good_eta = ExtendedTextAd("a", "b", "c", "d.", "e f", "http://asd.ca")
    assert good_eta.headline1 == "a"
    assert good_eta.headline2 == "b"
    assert good_eta.description == "c"
    assert good_eta.path1 == "d"
    assert good_eta.path2 == "ef"
    assert good_eta.final_url == "https://asd.ca"
    assert not good_eta.too_long()

    # path2 but no path1
    with pytest.raises(AssertionError):
        ExtendedTextAd("a", "b", "c", "", "e f", "http://asd.ca")

    # too long etas
    chars31 = "a" * 31
    chars81 = "a" * 81
    chars16 = "a" * 16
    with pytest.raises(AssertionError):
        ExtendedTextAd(chars31, "b", "c", "e", "f", "http://asd.ca")

    with pytest.raises(AssertionError):
        ExtendedTextAd("a", chars31, "c", "e", "f", "http://asd.ca")

    with pytest.raises(AssertionError):
        ExtendedTextAd("a", "b", chars81, "e", "f", "http://asd.ca")

    with pytest.raises(AssertionError):
        ExtendedTextAd("a", "b", "c", chars16, "f", "http://asd.ca")

    with pytest.raises(AssertionError):
        ExtendedTextAd("a", "b", "d", "e", chars16, "http://asd.ca")

    # missing protocol in url
    with pytest.raises(AssertionError):
        ExtendedTextAd("a", "b", "d", "e", chars16, "asd.ca")

    # http url
    http_eta = ExtendedTextAd("a", "b", "d", "e", "f", "https://asd.ca", https=False)
    assert http_eta.final_url == "http://asd.ca"


def test_keyword_final_url():
    from freedan import KeywordFinalUrl

    assert KeywordFinalUrl("https://asd.ca").url == "https://asd.ca"
    assert KeywordFinalUrl("http://asd.ca").url == "https://asd.ca"
    assert KeywordFinalUrl("https://asd.ca", https=False).url == "http://asd.ca"
    assert KeywordFinalUrl("http://asd.ca", https=False).url == "http://asd.ca"

    with pytest.raises(AssertionError):
        KeywordFinalUrl("asd.ca")


def test_keyword():
    from freedan.adwords_services.adwords_service import MICRO_FACTOR
    from freedan import Keyword, KeywordFinalUrl

    good_url = KeywordFinalUrl("https://asd.ca")
    good_kw = Keyword("test KW 1", "Exact", 1, good_url)
    assert good_kw.text == "test kw 1"
    assert good_kw.match_type == "EXACT"
    assert good_kw.max_cpc == 1.0
    assert good_kw.micro_max_cpc == 1000000
    assert isinstance(good_kw.final_url, KeywordFinalUrl)

    good_kw_no_conversion = Keyword("test KW 1", "Exact", 1, good_url)
    assert good_kw_no_conversion.max_cpc == 1.0

    # wrong match type
    with pytest.raises(AssertionError):
        Keyword("test KW 1", "Exat", 1, good_url)

    # too many words
    with pytest.raises(AssertionError):
        Keyword("1 2 3 4 5 6 7 8 9 10 11", "Exact", 1, good_url)

    # too long kw
    with pytest.raises(AssertionError):
        kw_text = "a" * 81
        Keyword(kw_text, "Exact", 1, good_url)

    # broad vs broad modified
    assert Keyword.is_real_broad("asd")
    assert Keyword.is_real_broad("asd adas")
    assert Keyword.is_real_broad("asd +adas")
    assert Keyword.is_real_broad("+asd adas")
    assert not Keyword.is_real_broad("+asd +adas")

    # broad vs broad modified
    assert Keyword.to_broad_modified("asd") == "+asd"
    assert Keyword.to_broad_modified("asd adas") == "+asd +adas"
    assert Keyword.to_broad_modified("asd +adas") == "+asd +adas"
    assert Keyword.to_broad_modified("+asd adas") == "+asd +adas"
    assert Keyword.to_broad_modified("+asd +adas") == "+asd +adas"


def test_shared_set_overview():
    import pandas as pd
    from tests import adwords_service
    from freedan import SharedSetOverview

    shared_set = SharedSetOverview(adwords_service)
    assert isinstance(shared_set.overview, pd.DataFrame)
