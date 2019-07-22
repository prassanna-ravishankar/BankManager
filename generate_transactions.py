from faker import Faker
from rstr import xeger
from faker.providers import BaseProvider

# TODO: Make the provider bank specific. Got to have the same bank id either
#       in the destination or the source.


class Provider(BaseProvider):
    def transaction(self):
        internal_faker = Faker()
        rule_gen_id = r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-' \
                            r'[0-9A-F]{4}-[0-9A-F]{12}$'
        date = internal_faker.iso8601()
        transaction_id = xeger(rule_gen_id)
        source_id = xeger(rule_gen_id)
        dest_id = xeger(rule_gen_id)
        amount = str(abs(internal_faker.pyfloat()))
        currency = internal_faker.currency_code()
        category = internal_faker.name().split(' ')[0]
        return ",".join([date, transaction_id, source_id,
                         dest_id, amount, currency, category])

transaction_faker = Faker()
transaction_faker.add_provider(Provider)

def generate_multiple_entries(nr_entries=100):
    return [transaction_faker.transaction()+"\n" for n in range(0, nr_entries)]

def generate_fake_transaction_log(filename="log.txt", nr_entries=100):
    with open(filename, "w") as f:
        f.writelines(generate_multiple_entries(nr_entries))


if __name__ == "__main__":
    generate_fake_transaction_log()
