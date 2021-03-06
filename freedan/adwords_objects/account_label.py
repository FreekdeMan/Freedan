class AccountLabel:
    def __init__(self, name, label_id):
        self.id = label_id
        self.name = name

    @classmethod
    def from_adwords_account_label(cls, adwords_acc_label):
        return cls(name=adwords_acc_label.name, label_id=adwords_acc_label.id)

    def __repr__(self):
        return "{name} ({id})".format(name=self.name, id=self.id)
