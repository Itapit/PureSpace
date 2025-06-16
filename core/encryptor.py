import os
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from core.helpers import ensure_directory_exists, safe_move_file, safe_create_directory, get_nonconflicting_path
from services.services import logger
from core.wrappers import with_dry_run

BLOCK_SIZE = AES.block_size  # 16 bytes

def encrypt_file(input_path, output_path, cipher, dry_run=False):
    if dry_run:
        logger.info(f"[DRY RUN] Would encrypt: {input_path} → {output_path}")
        return

    with open(input_path, 'rb') as f_in:
        data = f_in.read()
    padded_data = pad(data, BLOCK_SIZE)
    encrypted_data = cipher.encrypt(padded_data)

    ensure_directory_exists(os.path.dirname(output_path))
    with open(output_path, 'wb') as f_out:
        f_out.write(encrypted_data)

    logger.info(f"Encrypted: {input_path} → {output_path}")

def decrypt_file(input_path, output_path, cipher, dry_run=False):
    if dry_run:
        logger.info(f"[DRY RUN] Would decrypt: {input_path} → {output_path}")
        return

    with open(input_path, 'rb') as f_in:
        encrypted_data = f_in.read()
    decrypted_padded_data = cipher.decrypt(encrypted_data)
    data = unpad(decrypted_padded_data, BLOCK_SIZE)

    ensure_directory_exists(os.path.dirname(output_path))
    with open(output_path, 'wb') as f_out:
        f_out.write(data)

    logger.info(f"Decrypted: {input_path} → {output_path}")


def encrypt_directory(source_dir, key, iv, dry_run=False):
    parent_dir = Path(source_dir).parent
    encrypted_dir = safe_create_directory(parent_dir, f'encrypted_{Path(source_dir).name}')

    cipher = AES.new(key, AES.MODE_CBC, iv)

    for root, _, files in os.walk(source_dir):
        for file in files:
            full_input_path = Path(root) / file
            relative_path = full_input_path.relative_to(source_dir)
            full_output_path = encrypted_dir / relative_path

            output_path = get_nonconflicting_path(full_output_path)
            encrypt_file(str(full_input_path), str(output_path), cipher, dry_run=dry_run)



def decrypt_directory(source_dir, key, iv, dry_run=False):
    parent_dir = Path(source_dir).parent
    decrypted_dir = safe_create_directory(parent_dir, f'decrypted_{Path(source_dir).name}')

    cipher = AES.new(key, AES.MODE_CBC, iv)

    for root, _, files in os.walk(source_dir):
        for file in files:
            full_input_path = Path(root) / file
            relative_path = full_input_path.relative_to(source_dir)
            full_output_path = decrypted_dir / relative_path

            output_path = get_nonconflicting_path(full_output_path)
            decrypt_file(str(full_input_path), str(output_path), cipher, dry_run=dry_run)

# Note: Key must be a 64-character hexadecimal string (32 bytes) and IV a 32-character hex string (16 bytes).
# Example usage:
# key = bytes.fromhex(user_key_hex)
# iv = bytes.fromhex(user_iv_hex)
