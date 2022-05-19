[![all_workflow](https://github.com/KowComical/GlobalPowerUpdate-Kow/actions/workflows/all_workflow.yml/badge.svg?branch=master)](https://github.com/KowComical/GlobalPowerUpdate-Kow/actions/workflows/all_workflow.yml)
<a href="https://github.com/users/KowComical/projects/2"><img src="https://img.shields.io/badge/issues-project-blue"/></a>



# 数据情况
## 分能源
|||||||||
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|**[`Coal`](./image/Coal_generation_for_all_country.svg)**|**[`Gas`](./image/Gas_generation_for_all_country.svg)**|**[`Oil`](./image/Oil_generation_for_all_country.svg)**|**[`Nuclear`](./image/Nuclear_generation_for_all_country.svg)**|**[`Hydro`](./image/Hydro_generation_for_all_country.svg)**|**[`Solar`](./image/Solar_generation_for_all_country.svg)**|**[`Wind`](./image/Wind_generation_for_all_country.svg)**|**[`Other`](./image/Other_generation_for_all_country.svg)**|
### 所有能源
![](./image/Power_generation_for_all_country.svg)


### Other_Database
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[iea](./data/#global_rf/iea)**|**[monthly-electricity-statistics](https://www.iea.org/data-and-statistics/data-product/monthly-electricity-statistics)**|![](./image/updated/iea_cleaned.png)|`Monthly`|每月15号更新3个月前的数据|**[`Biqing`](https://github.com/cadagno)**<br>**[`Kow`](https://github.com/KowComical)**|
|**[bp](./data/#global_rf/bp)**|**[Statistical Review of World Energys](https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy.html)**|![](./image/updated/bp_cleaned.png)|`Yearly`|bp年度数据 爬虫没写|**[`Biqing`](https://github.com/cadagno)**<br>**[`Kow`](https://github.com/KowComical)**|
### Asian
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[China](./data/asia/china)**|**[中国电力企业联合会](https://cec.org.cn/menu/index.html?170)**|![](./image/updated/China.png)|`Daily`|未来会进一步完善爬虫|**[`Biqing`](https://github.com/cadagno)**<br>**[`Zhu Deng`](https://github.com/thuzhu)**<br>**[`Kow`](https://github.com/KowComical)**|
|**[India](./data/asia/india)**|**[POSOCO](https://posoco.in/reports/daily-reports/)**|![](./image/updated/India.png)|`Daily`|1天延迟|**[`Biqing`](https://github.com/cadagno)**<br>**[`Zhu Deng`](https://github.com/thuzhu)**<br>**[`Kow`](https://github.com/KowComical)**|
|**[Japan](./data/asia/japan)**|**[OCCTO](https://occtonet3.occto.or.jp/public/dfw/RP11/OCCTO/SD/LOGIN_login#)**|![](./image/updated/Japan.png)|`Hourly`|每月10号更新2个月前数据<br>用日本公司数据拆分的火电类型|**[`Biqing`](https://github.com/cadagno)**<br>**[`Zhu_Deng`](https://github.com/thuzhu)**<br>**[`Kow`](https://github.com/KowComical)**|
|**[Turkey](https://github.com/KowComical/GlobalPowerUpdate-Kow/issues/27)**||||已有源数据<br>还未更新||

### Africa
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[South Africa](./data/africa/south_africa)**|**[Eskom](https://www.eskom.co.za/dataportal/supply-side/station-build-up-for-the-last-7-days/)**|![](./image/updated/south_africa.png)|`Hourly`|跟网站申请要历史数据了<br>还未进行simulate|**[`Biqing`](https://github.com/cadagno)**<br>**[`Kow`](https://github.com/KowComical)**|

### Europe
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[EU27&UK](./data/europe/eu27_uk)**|**[Entsoe](https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/show)**<br>**[BMRS](https://www.bmreports.com/bmrs)**|![](./image/updated/Germany.png)|`Hourly`|UK用的是BMRS数据<br>9小时延迟|**[`Biqing`](https://github.com/cadagno)**<br>**[`Zhu Deng`](https://github.com/thuzhu)**<br>**[`Kow`](https://github.com/KowComical)**|
|**[Russia](./data/europe/russia)**|**[EMRES](https://emres.cn)**|![](./image/updated/Russia.png)|`Hourly`|最后一个月数据是从bp simulated的<br>后续还要再修正拆分火电<br>Hourly 并不能正确反映太阳能数据|**[`Zhu Deng`](https://github.com/thuzhu)**<br>**[`Kow`](https://github.com/KowComical)**|
|**[Ukraine](https://github.com/KowComical/GlobalPowerUpdate-Kow/issues/23)** ||||还未更新||

### North_America
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[United States](./data/n_america/us)**|**[EIA](https://www.eia.gov/electricity/)**|![](./image/updated/US.png)|`Hourly`|24小时左右延迟|**[`Biqing`](https://github.com/cadagno)**<br>**[`Zhu Deng`](https://github.com/thuzhu)**<br>**[`Kow`](https://github.com/KowComical)**|


### Sorth_America
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[Brazil](./data/s_america/brazil)**|**[ONS](http://www.ons.org.br/Paginas/resultados-da-operacao/historico-da-operacao)**|![](./image/updated/Brazil.png)|`Hourly`|72小时左右延迟|**[`Biqing`](https://github.com/cadagno)**<br>**[`Zhu Deng`](https://github.com/thuzhu)**<br>**[`Kow`](https://github.com/KowComical)**|

### Oceania
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[Austrlia](https://github.com/KowComical/GlobalPowerUpdate-Kow/issues/12)**||||还未更新||

### ROW
|Name|Source|Date_Updated|Resolution|Description|Author|
|:-:|:-:|:-:|:-:|:-:|:-:|
|**[ROW](https://github.com/KowComical/GlobalPowerUpdate-Kow/issues/11)**||||还未更新||


