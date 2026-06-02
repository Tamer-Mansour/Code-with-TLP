# Secure Boot and the Chain of Trust

Secure Boot is a UEFI feature that cryptographically verifies each component in the boot path before executing it. Without it, an attacker with physical or administrative access can replace the bootloader with malware that runs before the OS — and before any antivirus or endpoint detection tool — every time the machine boots.

## The Threat: Boot-Level Attacks

- **Bootkit** — malware that infects the MBR, VBR, or EFI executable; persists across OS reinstalls
- **Evil maid attack** — attacker with brief physical access replaces the bootloader on an unattended machine
- **Rollback attack** — downgrade to an older, vulnerable version of a signed component

Secure Boot defends against all of these by requiring a valid cryptographic signature at each boot stage.

**Interview answer:** Secure Boot uses a chain of cryptographic signatures — UEFI firmware verifies the bootloader, the bootloader verifies the kernel, and the kernel verifies modules — so that only trusted code runs during boot.

## Key Concepts

### Databases Stored in UEFI NVRAM

| Variable | Contents |
|----------|---------|
| **PK** (Platform Key) | One key; owned by the OEM; root of trust |
| **KEK** (Key Exchange Keys) | Keys that may sign updates to db/dbx |
| **db** (Allowed signatures) | Certificates/hashes of trusted EFI executables |
| **dbx** (Forbidden signatures) | Revocation list; blocks known-bad binaries |

### Chain of Trust

```
UEFI Firmware (trusted by silicon/OEM)
        │  verifies signature of
        ▼
Bootloader (e.g., grubx64.efi — signed by distro key in db)
        │  verifies signature of
        ▼
Kernel (e.g., vmlinuz — signed by distro key)
        │  verifies signature of
        ▼
Kernel Modules (.ko files — signed with per-build key)
```

Each link in the chain must pass; if any signature is absent or invalid, UEFI (or the bootloader) halts execution and displays an error.

## How It Works in Practice

### Signing a Bootloader

```bash
# Generate a Machine Owner Key (MOK) for custom kernels
$ openssl req -new -x509 -newkey rsa:2048 \
    -keyout MOK.key -out MOK.crt -days 3650 \
    -subj "/CN=My Secure Boot Key/"

# Sign a kernel module with the MOK
$ /usr/src/linux-headers-$(uname -r)/scripts/sign-file \
    sha256 MOK.key MOK.crt my_driver.ko

# Enroll the MOK into the MOK database (requires reboot + MokManager prompt)
$ mokutil --import MOK.crt
```

### How Distros Handle Secure Boot

Most Linux distributions use a **shim** — a tiny EFI executable pre-signed by Microsoft (whose certificate is in most OEM `db` databases). The shim then:

1. Verifies the distro's own bootloader (`grubx64.efi`) against the distro's certificate embedded in the shim
2. GRUB verifies the kernel
3. The kernel enforces module signing

```
db contains: Microsoft Corporation UEFI CA
             (Microsoft signs shim.efi for each distro)
shim.efi  → verifies grubx64.efi (signed by Ubuntu/Red Hat/etc.)
grubx64.efi → verifies vmlinuz (signed by distro)
```

### Enabling/Disabling on a Machine

```bash
# Check Secure Boot status
$ mokutil --sb-state
SecureBoot enabled

# Or via sysfs
$ cat /sys/firmware/efi/efivars/SecureBoot-*
# Returns 5 bytes; byte [4] = 1 if enabled

# View enrolled keys
$ mokutil --list-enrolled
```

## Measured Boot and TPM

Secure Boot *prevents* untrusted code from running. **Measured Boot** goes further: it *records* what ran.

The **TPM** (Trusted Platform Module) contains **Platform Configuration Registers (PCRs)** — 24 hash registers that can only be extended (new value = SHA256(old value ∥ measurement)), never overwritten arbitrarily.

Each boot component measures the next:

| PCR | Measured content |
|-----|-----------------|
| 0 | UEFI firmware executable code |
| 1 | UEFI firmware configuration |
| 4 | Boot Manager / bootloader |
| 7 | Secure Boot policy state |
| 8–15 | GRUB, kernel command line, initrd (if configured) |

BitLocker (Windows) and LUKS with TPM unlocking (Linux) use PCR values as part of the key-sealing policy: the TPM releases the disk encryption key only when the PCR values match the expected boot configuration.

```bash
# Read current TPM PCR values (Linux, tpm2-tools)
$ tpm2_pcrread sha256:0,1,4,7
sha256:
  0 : 0x3A3F780F11A4B49969FCAA80CD6E3957C33B2275...
  1 : 0x6DF37B7A...
  4 : 0xABCD1234...
  7 : 0x00000000... (if Secure Boot is disabled)
```

## Pitfalls and Limitations

- **Secure Boot only covers the boot path** — once the OS is running, an attacker with root can load unsigned modules (if enforcement is off) or install kernel backdoors via other means.
- **Custom kernel builds require MOK enrollment** — developers who build their own kernels must enroll their signing key or disable Secure Boot.
- **CSM disables Secure Boot** — enabling legacy BIOS compatibility mode (CSM) requires turning off Secure Boot.
- **dbx must be kept current** — revoked but still-signed bootloaders remain dangerous if `dbx` is not updated. The "BootHole" vulnerability (2020) showed that a bug in GRUB could bypass Secure Boot; the fix required distributing a `dbx` update that blocked all old GRUB versions.

## Common Pitfalls

- Assuming Secure Boot means the *running* OS is secure — Secure Boot only validates the boot path, not runtime kernel integrity.
- Forgetting that `shim` must match the specific bootloader — replacing GRUB with a different version without re-signing breaks the shim's verification.
- Not enrolling MOK after generating it — the key must be registered before the next boot for `mokutil --import` to take effect.
