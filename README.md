# econt_test-vectors
Test vectors for ECON-T testing

## How to generate input data

In ECON-T emulator:
```
# go to main directory
cd econt_sw/ECONT_Emulator/
# run emulator taking an `init.yaml` file in an input-directory
# RPT: repeater, TS: threshold sum, BC: best choice, STC: super trigger cell
# add naming to these directories in case any of the i2c configurations (e.g. calib values, MUX, STC type) changes.
python RunFromYamlInput.py --inputDir ../econt_sw/configs/test_vectors/randomPatternExpInTC/RPT/
```

## How to unpack data
For input data:
```
# with generic unpacking
python utils/unpack.py -i counterPatternInTC/RPT/testInput.csv --sim --algo input --nrows 4
# or:
python utils/parseInput.py --inputDir counterPatternInTC/RPT/ --fileName testInput.csv -v
```

For Repeater data:


For Threshold Sum data: