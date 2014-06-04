
from settings import *
from tool_box import *

declare -i filenr
filenr=100

###############################################################################
#
# Attempted open of non-existent file; O_TRUNC
#
###############################################################################

# Open read-only
echo "TEST$filenr: Open O_TRUNC|O_RDONLY"
file=$testdir/no_foo$((filenr++))$termslash

open_file -t -r $file -E ENOENT
open_file -t -r $file -E ENOENT

# Open write-only and overwrite
echo "TEST$filenr: Open O_TRUNC|O_WRONLY"
file=$testdir/no_foo$((filenr++))$termslash

open_file -t -w $file -E ENOENT
open_file -t -w $file -E ENOENT

# Open write-only and append
echo "TEST$filenr: Open O_TRUNC|O_APPEND|O_WRONLY"
file=$testdir/no_foo$((filenr++))$termslash

open_file -t -a $file -E ENOENT
open_file -t -a $file -E ENOENT

# Open read/write and overwrite
echo "TEST$filenr: Open O_TRUNC|O_RDWR"
file=$testdir/no_foo$((filenr++))$termslash

open_file -t -r -w $file -E ENOENT
open_file -t -r -w $file -E ENOENT

# Open read/write and append
echo "TEST$filenr: Open O_TRUNC|O_APPEND|O_RDWR"
file=$testdir/no_foo$((filenr++))$termslash

open_file -t -r -a $file -E ENOENT
open_file -t -r -a $file -E ENOENT