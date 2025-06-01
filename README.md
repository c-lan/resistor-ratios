# [Get data here](ratios.txt)

Lists (hopefully) all possible voltage divider arrangements from 4-8 identical resistors and ranks them based on sensitivity to individual resistor value changes.
Error figures represent change of voltage ratio relative to change of resistance of a network element, in percent - the closer to zero the better. Plus sign indicates the ratio goes up when the resistor goes up. The sign and magnitude could be useful for optimal resistor interleaving.
Error of 22 means the ratio will change by 22ppm if the most significant resistor in the circuit changes by 100ppm
Average error is defined as an arithmetic mean of absolute values of errors caused by changing resistor values in the circuit one by one.
Rin, Rout is the input and output resistance of the divider

## How to read the netlist
Each entry on the list is a resistor of equal value. `vin_0` means it's connected between a node named `vin` and a node named `0`. You apply a voltage at `vin` and get a voltage divided by the specified ratio on node `out`.
![Example netlist](example.png?raw=true "Example netlist")

## How to recalculate
The repository contains pre-generated data for 8 resistors since that is the most common model and the text file is still easy to navigate in the browser or text editor. The script supports larger data sets, for example less common 12-resistor arrays. Generating the list for N=12 takes about 5 minutes and the time/memory usage scales exponentially
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
apt install chicken-bin
# edit the bottom of the file to generate more combinations (up to 11 when calculating 12-resistor dividers)
csi -s isokawa.scm | python3 convert.py > circuits.txt
python3 run.py > ratios.txt
python3 find.py 1.4 1.5 -n 6 7 8 -c 2
```

## Citations
KHAN, S.A. Farey sequences and resistor networks. Proc Math Sci 122, 153–162 (2012). https://doi.org/10.1007/s12044-012-0066-7  
ISOKAWA Yukinao. Listing up Combinations of Resistances. 鹿児島大学教育学部研究紀要. 自然科学編 = Bulletin of the Faculty of Education, Kagoshima University. Natural science. 67:2015年度,p.1-8. https://ndlsearch.ndl.go.jp/books/R000000004-I027464713
