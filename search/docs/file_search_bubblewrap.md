File Search - Bubblewrap

Here's how to safely use **Bubblewrap (bwrap)** in Linux to run a program or analyze files inside a highly restricted sandbox, where the process can only see the specific files/folders you explicitly allow.

Bubblewrap is the same low-level sandboxing tool that Flatpak uses under the hood. It's very powerful and doesn't require root privileges.

### Goal
Run a tool (e.g., `strings`, `exiftool`, `clamscan`, `file`, custom Python script, etc.) on potentially malicious files, but completely isolate it so it can't access your real home, network, etc.

### Basic Example: Analyze a single suspicious file safely

```bash
# Suppose you have a suspicious file: ~/Downloads/mystery.exe

bwrap \
  --ro-bind /usr /usr \                  # read-only access to system binaries/libs
  --dir /tmp \                            # empty writable tmp
  --proc /proc \                          # proc filesystem
  --dev /dev \                            # basic devices (null, zero, tty, etc.)
  --ro-bind "/home/user/Downloads/mystery.exe" "/file-to-analyze" \  # only this file
  --unshare-all \                         # isolate everything (pid, net, user, etc.)
  --die-with-parent \                     # die if parent dies
  --new-session \
  /usr/bin/strings /file-to-analyze       # or any tool you want: file, exiftool, python script, etc.
```

### More realistic example: Run multiple analysis tools on a whole directory

```bash
mkdir -p ~/sandbox/root   # temporary empty root for the sandbox

bwrap \
  --ro-bind /usr /usr \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /bin /bin \
  --ro-bind /etc /etc \
  --bind ~/sandbox/root /root \           # fake empty $HOME so tools don't complain
  --bind ~/sandbox/root /home \
  --bind ~/sandbox/root /var \
  --tmpfs /tmp \
  --tmpfs /run \
  --proc /proc \
  --dev /dev \
  --ro-bind "~/Suspicious_Files" "/samples" \   # the directory you want to analyze
  --unshare-all \
  --share-net \                         # optional: remove this line to block network too
  --die-with-parent \
  --new-session \
  /bin/bash                                        # drops you into an interactive shell
```

Inside the sandbox you can now safely run:

```bash
file /samples/*
strings /samples/bad.exe
exiftool /samples/photo.jpg
python3 myscript.py /samples/
clamscan -r /samples/
```

The process literally cannot see anything outside `/samples` and the read-only system directories.

### Even stricter (recommended for untrusted binaries)

If you want to run an unknown binary for analysis (dynamic analysis), make it super locked down):

```bash
bwrap \
  --ro-bind /usr /usr \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /bin /bin \
  --dir /tmp \
  --proc /proc \
  --dev /dev \
  --ro-bind "./malware.exe" /malware.exe \
  --unshare-all \               # no network, no IPC, no nothing
  --seccomp 10 \                # apply seccomp filter (10 = load filter from fd 10)
  10<syscall-filter.scmp \      # optional extra seccomp filter file
  --die-with-parent \
  /malware.exe                  # it runs but can't touch your real system
```

### Install bubblewrap (if not present)

```bash
# Debian/Ubuntu
sudo apt install bubblewrap

# Fedora
sudo dnf install bubblewrap

# Arch
sudo pacman -S bubblewrap
```

### Quick one-liners for common tools

```bash
# Just run 'file' on everything in a folder
bwrap --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 \
      --dev /dev --proc /proc --tmpfs /tmp \
      --ro-bind "./samples" /samples --unshare-all --die-with-parent \
      file /samples/*

# Run VirusTotal's "vt" CLI tool safely
bwrap --ro-bind /usr /usr --ro-bind ~/.local/bin/vt /vt \
      --ro-bind "./file.exe" /f --tmpfs /tmp --dev /dev \
      --unshare-pid --unshare-uts --share-net \
      /vt file /f
```

Bubblewrap is one of the safest and most flexible ways to analyze untrusted files on Linux without using full VMs or containers. Use it whenever you're dealing with potentially malicious downloads.

sudo apt install bubblewrap

cd search


bwrap --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 \
      --dev /dev --proc /proc --tmpfs /tmp \
      --ro-bind "./docs" /docs --unshare-all --die-with-parent \
      file /docs/*

--- 

response

docs/api_server.md:                Unicode text, UTF-8 text
docs/architecture.md:              Unicode text, UTF-8 text
docs/architecute-diagram.drawio:   ASCII text, with very long lines (317)
docs/architecute-diagram.jpg:      JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 1156x551, components 3
docs/desing_ingestion_pipeline.md: Unicode text, UTF-8 text
docs/file_search_bubblewrap.md:    ASCII text
docs/full_docs.md:                 Unicode text, UTF-8 text
docs/implementation.md:            Unicode text, UTF-8 text
docs/ingestion_implemenation.md:   Unicode text, UTF-8 text
docs/production_checklist.md:      Unicode text, UTF-8 text
docs/steps.md:                     Unicode text, UTF-8 text