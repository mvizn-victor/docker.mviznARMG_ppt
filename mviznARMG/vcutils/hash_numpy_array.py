#version: 1.0.0

def hash_numpy_array(array):
    import hashlib
    # Convert the array to bytes
    array_bytes = array.tobytes()
    # Create a hash object
    hash_object = hashlib.sha256()
    # Update the hash object with the bytes
    hash_object.update(array_bytes)
    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()
    return hash_hex
