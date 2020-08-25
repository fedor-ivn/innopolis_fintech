from eth_hash.auto import keccak
from py_ecc.secp256k1 import ecdsa_raw_sign

n = 5


def main(lines):
    for i in range(0, n * 2, 2):
        private_key_str = lines[i]
        private_key_bytes = int(private_key_str, base=16).to_bytes(32, 'big')

        message = lines[i + 1]
        message_bytes = message.encode()

        message_hash = keccak(message_bytes)
        v, r, s = ecdsa_raw_sign(message_hash, private_key_bytes)
        print(*map(lambda j: hex(j)[2:], [v, r, s]), sep='\n')


if __name__ == '__main__':
    with open('../dataset_59926_6 (1).txt') as file:
        file_lines = file.read().split('\n')
        main(file_lines)
