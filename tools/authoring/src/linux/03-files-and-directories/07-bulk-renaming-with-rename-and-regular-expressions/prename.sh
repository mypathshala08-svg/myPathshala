# Verification stand-in for Ubuntu's Perl rename (file-rename), used ONLY at build time because the
# build machine cannot install the 'rename' package. It evaluates the same Perl expression on each name,
# like File::Rename does, and prints the same -n / -v messages. Outputs made with it are labelled
# "typical output (verified with the same Perl expression)" on the page.
rename() {
  local n=0 v=0
  while [[ $1 == -* ]]; do case $1 in -n|--nono) n=1;; -v|--verbose) v=1;; -f|--force) ;; esac; shift; done
  local e=$1; shift
  perl -e '
    my ($n, $v, $e, @f) = @ARGV;
    for (@f) { my $o = $_; eval $e; die $@ if $@; next if $_ eq $o;
      if ($n) { print "rename($o, $_)\n"; next }
      if (-e $_) { print STDERR "$o not renamed: $_ already exists\n"; next }
      rename($o, $_) or die "rename $o: $!"; print "$o renamed as $_\n" if $v }' "$n" "$v" "$e" "$@"
}
