# [Get data here](ratios.txt)

Lists (hopefully) all possible voltage divider arrangements from 4-8 identical resistors and ranks them based on sensitivity to individual resistor value changes.
Error figures represent change of voltage ratio relative to change of resistance of a network element, in percent - the lower the better.  
Max error of 22 means the ratio will change by 22ppm if the most significant resistor in the circuit changes by 100ppm
Average error is defined as an arithmetic mean of errors caused by changing resistor values in the circuit one by one.
Rin, Rout is the input and output resistance of the divider

## How to read the netlist
Each entry on the list is a resistor of equal value. `vin_0` means it's connected between a node named `vin` and a node named `0`. You apply a voltage at `vin` and get a voltage divided by the specified ratio on node `out`.
![Example netlist](example.png?raw=true "Example netlist")

## Citations
KHAN, S.A. Farey sequences and resistor networks. Proc Math Sci 122, 153–162 (2012). https://doi.org/10.1007/s12044-012-0066-7  
ISOKAWA Yukinao. Listing up Combinations of Resistances. 鹿児島大学教育学部研究紀要. 自然科学編 = Bulletin of the Faculty of Education, Kagoshima University. Natural science. 67:2015年度,p.1-8. https://ndlsearch.ndl.go.jp/books/R000000004-I027464713
