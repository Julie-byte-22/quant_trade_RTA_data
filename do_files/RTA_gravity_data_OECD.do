
************** Report Master QUEA M2: Quantitative International Trade ********* 

* This project aims to estimate the effect of data-related RTAs on trade 

* Data source: The database reports bilateral trade, including international and
*              intra-national trade, at the aggregated manufacturing level for 51 
*			   countries for the period 2010 - 2019, provided by Farid Toubal, 
*			   ITC and the TAPED database. Standard gravity variables were provided
*		       as part of the dataset shared in the course. 

******************************* PRELIMINARY STEP *******************************

* Clear memory and set parameters
	clear all
	set more off
	clear matrix
	set memory 500m
	set matsize 8000
	set maxvar 30000
	set maxiter 10
	
* Set directory path, where "$input" refers to the path of the main folder 
	cd "S:\Data\_Users\Julia_S\project_s"
		
* Close and create log	
	capture log close
	log using "S:\Data\_Users\Julia_S\project_s\RTA_data_OECD.log", text replace

* Install or update the ppml command if necessary	
	*ssc install ppml
	*ssc install ppml
	*ssc install ppml, replace(directory= "\\Client\H$\Documents\studies\Paris Dauphine 2022\Master Quantitative Economics\trade_22\report\data")

* Install or update the ppml_panel_sg command if necessary	
	*ssc install ppml_panel_sg

* Install or update the hdfe command used by the ppml_panel_sg command if necessary	
	*ssc install hdfe

* Install or update the esttab command if necessary
	*findit esttab
	
************************* Generate variables **********************************
* Open the database 
	import delimited "gravity_final_OECD.csv", clear

*Describe the data
		describe

* Create the dependent variable	for OLS regression
		gen ln_trade = ln(trade)
		
*Create the log variable of distance
		gen ln_dist = ln(dist)
		replace ln_dist = 0 if missing(ln_dist) 
		

* Create exporter-time fixed effects
		egen exp_time = group(iso3_i year)
			quietly tabulate exp_time, gen(EXPORTER_TIME_FE)

* Create importer-time fixed effects
		egen imp_time = group(iso3_j year)
			quietly tabulate imp_time, gen(IMPORTER_TIME_FE)
			
*Country pair fixed effects have been created in python as STATA could not handle the number of values
	* Create pair fixed effects
		summarize pair_id
			replace pair_id = pair_id + 100000 if iso3_i == iso3_j
			quietly tabulate pair_id, gen(PAIR_FE)

*Create lead variables
	gen rta_data_lead3 = rta_data + rta_data[_n-3]
	gen rta_data_lead4 = rta_data + rta_data[_n-4]

*Create lag variables
	gen rta_data_lag4 = rta_data[_n-4] 
	gen rta_data_lag8 = rta_data[_n-8] 
	gen rta_data_lag12 = rta_data[_n-12] 


*********************************** ANALYSIS ***********************************

*********** (a) Standard RTA estimates with international trade only ***********

* Estimate the gravity model with the OLS estimator
		regress ln_trade EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data if iso3_i != iso3_j, cluster(pair_id)

* Store the results
		estimates store ols
		
					
* Perform the RESET test
                                predict fit, xb
                                                generate fit2 = fit^2
                                regress ln_trade EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data fit2 if iso3_i != iso3_j, cluster(pair_id)
                                                test fit2 = 0
                                                drop fit*


* Estimate the gravity model with the PPML estimator and store the results
		ppmlhdfe trade EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data if iso3_i != iso3_j, cluster(pair_id)
			estimates store ppml
			
* Perform the RESET test
                                predict fit, xb
                                                generate fit2 = fit^2
                                ppmlhdfe trade EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data fit2 if iso3_i != iso3_j, cluster(pair_id)
                                                test fit2 = 0
                                                drop fit*
		
************** (b)	Addressing potential domestic trade diversion **************

* Estimate the gravity model with the PPML estimator by considering
* intra-national trade as well as international trade and store the results
		ppmlhdfe trade EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data, cluster(pair_id)
			estimates store ppml_intra
			
			
* Perform the RESET test
                                predict fit, xb
                                                generate fit2 = fit^2
                                ppmlhdfe trade EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data fit2, cluster(pair_id)
                                                test fit2 = 0
                                                drop fit*
 

***************** (c) Addressing potential endogeneity of RTAs *****************

* Estimate the gravity model with the PPML estimator by applying the
* average treatment effects (country fixed effects) and store the results

		*ppmlhdfe trade PAIR_FE* EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data, cluster(pair_id)
		
		ppml_panel_sg trade rta rta_data, ex(iso3_i) im(iso3_j) y(year) sym cluster(pair_id) 
			estimates store ppml_intra_cfe
			

***** (d) Testing for potential "reverse causality" between trade and RTAs *****

* Estimate the gravity model with the PPML estimator and store the results
		*ppmlhdfe trade PAIR_FE* EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data rta_data_lead3, cluster(pair_id)
		ppml_panel_sg trade rta rta_data rta_data_lead3, ex(iso3_i) im(iso3_j) y(year) sym cluster(pair_id) 
			estimates store ppml_lead
	
****** (e) Addressing potential non-linear and phasing-in effects of RTAs ******

* Estimate the gravity model with the PPML estimator and store the results
		*ppmlhdfe trade PAIR_FE* EXPORTER_TIME_FE* IMPORTER_TIME_FE* ln_dist contig col comcol rta rta_data rta_data_lag4 rta_data_lag8 rta_data_lag12, cluster(pair_id)
		
		ppml_panel_sg trade rta rta_data rta_data_lag4 rta_data_lag8 rta_data_lag12, ex(iso3_i) im(iso3_j) y(year) sym cluster(pair_id) 
			estimates store ppml_lags 
			
****** Calculating the tariff equivalent elasticity using elasticity of substitution from literature

scalar sigma = 5 
scalar TariffEquivalentRTA_1 = (exp(_b[rta_data]/(-sigma))-1)*100
			
******************************* EXPORT ESTIMATES *******************************

* Export estimates in Excel format
		esttab ols ppml ppml_intra ppml_intra_cfe ppml_lead ppml_lags using "Data_RTAsEffects_OECD.csv", append title(Estimating the Effects of Regional Trade Agreements) mtitles(OLS PPML INTRA PAIRFE LEAD PHSNG) b(3) se(3) scalars(N r2) star(+ 0.10 * .05 ** .01) drop(EXPORTER_TIME_FE* IMPORTER_TIME_FE*) staraux nogaps

		
* Save the data used for this application 
	save "data_RTA_OECD.dta", replace
*/