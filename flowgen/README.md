# flowgen

These scripts takes and input flow accumulation raster and aggregates it by a factor of 15. For instance, a 15 arcsecond accumulation file is aggregated to 1/16th degree.

Compile the binaries:

```bash
make
```

Run the conversion:

```bash
make_rout.sh <accumulation_file.asc> <output_direction_file.asc>
```
