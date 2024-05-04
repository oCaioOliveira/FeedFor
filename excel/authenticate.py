from O365 import Account


def get_account():
    credentials = (
        "b9b91e6d-1e45-4ab3-8765-2e7b83a73ce4",
        "cUQ8Q~VUMgqdgdFBkdwkJflPURmpsDw.5iTGtbtF",
    )

    account = Account(
        credentials,
        auth_flow_type="credentials",
        tenant_id="27330bd3-e8db-4326-befc-3c1ded0069fd",
    )
    if account.authenticate():
        print("Authenticated!")
        return account
