# attys-plot

Python script which
filters and plots the tsv files recorded by attys-scope and the 
[Attys](http://www.attys.tech).

`attys-plot.py` first loads the raw unfiltered data. Then
select the filter functions such as low, high or bandstop
filters and plot the results.

![alt tag](selection_window.png)
![alt tag](browser_window.png)

## Python requirements

```
pip install PyQtChart
pip install plotly
```

## How to run

Just run `attys-plot.py` with:

```
python attys-plot.py
```
