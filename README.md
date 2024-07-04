# async-httpd-data-collector

Interface handling the communication between sensory data-emitting devices, InfluxDB and the user.

The most important object that a user would use is `DatabseInterface` within `ahttpdc.reads.interface` module.
This class facilitates the communication between the fetcher and the querying apis of InfluxDB.

In order to control fetching, there are two methods:

* `interface.enable_fetching()`;
* `interface.disable_fetching()`.

Those methods control the thread within which fetching process is contained.

You can query data from the database using methods with `query_` prefix. For now there are three:

* `interface.query_latest()`, which queries the lastest measurement;
* `interface.query_historical()`, which queries data from a given time range or relative time (eg. -3h);
* `interface.query()`, which can takes user's given query as an argument.

Some examples will be presented below:

# 1.1 Connecting to the database


```python
import json
from ahttpdc.reads.interface import DatabaseInterface

# load the secrets
with open('../../../secrets/secrets.json', 'r') as f:
    secrets = json.load(f)

# define sensors
sensors = {
    'bmp180': ['altitude', 'pressure', 'seaLevelPressure'],
    'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
    'ds18b20': ['temperature'],
    'dht22': ['humidity'],
}

# define the interface to the database
interface = DatabaseInterface(
    secrets['host'],
    secrets['port'],
    secrets['token'],
    secrets['organization'],
    secrets['bucket'],
    sensors,
    secrets['dev_ip'],
    80,
    secrets['handle'],
)
```

### 1.2 Extracting the dataframe from the database


```python
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# if there is readings.csv file, load it
# if not - create it
readings_path = Path('../data/readings.csv')
if readings_path.is_file():
    sensor = pd.read_csv(readings_path)
else:
    sensor = await interface.query_historical('-30d')
    sensor.to_csv(readings_path)
```


```python
sensor
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>aceton</th>
      <th>alcohol</th>
      <th>altitude</th>
      <th>co</th>
      <th>co2</th>
      <th>humidity</th>
      <th>nh4</th>
      <th>pressure</th>
      <th>seaLevelPressure</th>
      <th>temperature</th>
      <th>toulen</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2024-05-16 17:43:59.196399+00:00</td>
      <td>0.41</td>
      <td>1.17</td>
      <td>149.92</td>
      <td>3.38</td>
      <td>402.54</td>
      <td>37.4</td>
      <td>3.93</td>
      <td>999.35</td>
      <td>1017.31</td>
      <td>24.40</td>
      <td>0.48</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2024-05-16 17:44:01.768738+00:00</td>
      <td>0.47</td>
      <td>1.32</td>
      <td>149.76</td>
      <td>3.94</td>
      <td>402.84</td>
      <td>30.5</td>
      <td>4.33</td>
      <td>997.61</td>
      <td>1015.56</td>
      <td>24.03</td>
      <td>0.55</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2024-05-16 17:44:03.255309+00:00</td>
      <td>0.96</td>
      <td>2.62</td>
      <td>149.54</td>
      <td>9.16</td>
      <td>405.25</td>
      <td>49.1</td>
      <td>7.35</td>
      <td>999.14</td>
      <td>1017.08</td>
      <td>23.16</td>
      <td>1.15</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2024-05-16 17:44:04.618203+00:00</td>
      <td>0.30</td>
      <td>0.86</td>
      <td>149.38</td>
      <td>2.32</td>
      <td>401.94</td>
      <td>32.9</td>
      <td>3.10</td>
      <td>999.09</td>
      <td>1017.02</td>
      <td>23.05</td>
      <td>0.35</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2024-05-16 17:44:05.954714+00:00</td>
      <td>1.31</td>
      <td>3.50</td>
      <td>149.37</td>
      <td>13.13</td>
      <td>406.82</td>
      <td>48.8</td>
      <td>9.21</td>
      <td>998.04</td>
      <td>1015.93</td>
      <td>23.92</td>
      <td>1.57</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>284122</th>
      <td>2024-05-21 14:42:57.894312+00:00</td>
      <td>1.35</td>
      <td>3.62</td>
      <td>150.08</td>
      <td>13.68</td>
      <td>407.03</td>
      <td>47.6</td>
      <td>9.46</td>
      <td>998.85</td>
      <td>1016.81</td>
      <td>24.35</td>
      <td>1.63</td>
    </tr>
    <tr>
      <th>284123</th>
      <td>2024-05-21 14:42:59.277937+00:00</td>
      <td>1.08</td>
      <td>2.92</td>
      <td>149.87</td>
      <td>10.48</td>
      <td>405.79</td>
      <td>49.3</td>
      <td>8.00</td>
      <td>998.58</td>
      <td>1016.53</td>
      <td>23.41</td>
      <td>1.29</td>
    </tr>
    <tr>
      <th>284124</th>
      <td>2024-05-21 14:43:00.594968+00:00</td>
      <td>0.38</td>
      <td>1.09</td>
      <td>149.97</td>
      <td>3.09</td>
      <td>402.38</td>
      <td>33.8</td>
      <td>3.71</td>
      <td>999.59</td>
      <td>1017.54</td>
      <td>24.88</td>
      <td>0.44</td>
    </tr>
    <tr>
      <th>284125</th>
      <td>2024-05-21 14:43:01.918239+00:00</td>
      <td>1.41</td>
      <td>3.77</td>
      <td>150.13</td>
      <td>14.38</td>
      <td>407.29</td>
      <td>44.4</td>
      <td>9.76</td>
      <td>998.51</td>
      <td>1016.48</td>
      <td>23.54</td>
      <td>1.70</td>
    </tr>
    <tr>
      <th>284126</th>
      <td>2024-05-21 14:43:03.248095+00:00</td>
      <td>1.24</td>
      <td>3.32</td>
      <td>150.50</td>
      <td>12.29</td>
      <td>406.50</td>
      <td>48.8</td>
      <td>8.84</td>
      <td>998.85</td>
      <td>1016.85</td>
      <td>22.44</td>
      <td>1.49</td>
    </tr>
  </tbody>
</table>
<p>284127 rows × 12 columns</p>
</div>



