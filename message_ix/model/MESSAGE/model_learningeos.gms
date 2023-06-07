Parameters
  cap_new2(node,tec,year_all2)        'annual newly installed capacity'
  bin_cap_new(node,tec,year_all2)     'binary of newly installed capacity'
  inv_cost_ref(node,tec)              'initial capex' ;
inv_cost_ref(node,tec) = 1500;

*$ontext
SETS
  size           'size'  / small, medium, large / ;

ALIAS (size,size2);
PARAMETERS
  cap_new2(node,tec,year_all2)        'annual newly installed capacity'
  bin_cap_new(node,tec,year_all2)     'binary of newly installed capacity'
  rho(tec)                            'economy of scale parameter'            / wind_ppl      1.0       / #0.8
  b(tec)                              'technology cost learning parameter'    / wind_ppl      0.0     / #0.9
  u(tec,size)                                'unit size'
         / wind_ppl.small      5
           wind_ppl.medium     10
           wind_ppl.large      50     /
  inv_cost_ref(node,tec)              'initial capex'
  nbr_unit_ref(tec)                   'initial number of unit'                / wind_ppl      100     /
  u_ref(tec)                          'reference size'                        / wind_ppl      5       / ;
inv_cost_ref(node,tec) = 1500;
*$offtext
SCALAR hist_length                       the length of historical periods;
hist_length = card(year_all2) - card(model_horizon);

VARIABLES
  NBR_UNIT(node,tec,size,year_all2)   number of units for each size every year
  CAPEX_TEC(node,tec,year_all2)       capital cost in dollar per kW
  OBJECT                                 objective function ;

POSITIVE VARIABLES
  NBR_UNIT ;

EQUATIONS
  OBJECTIVE_INNER        total investment cost
  CAP_NEW_BALANCE        installed capacity balance
  CAPEX_ESTIMATE         estimating average capex
  INITIAL_YEAR          annual investment cost
  NO_BUILT_YEAR          annual investment cost
;


OBJECTIVE_INNER..                        OBJECT =e= sum((node,tec,year_all2), CAPEX_TEC(node,tec,year_all2)*cap_new2(node,tec,year_all2)) ;
CAP_NEW_BALANCE(node,tec,year_all2).. sum(size, NBR_UNIT(node,tec,size,year_all2)*u(tec,size)) =e= cap_new2(node,tec,year_all2) ;
CAPEX_ESTIMATE(node,tec,year_all2)..  CAPEX_TEC(node,tec,year_all2)*cap_new2(node,tec,year_all2) =g= sum(size,inv_cost_ref(node,tec)
                                              * NBR_UNIT(node,tec,size,year_all2)*u(tec,size)
                                              * [(((sum((size2,year_all3)$(ord(year_all3) le (ord(year_all2)-1) and ord(year_all3) gt hist_length), NBR_UNIT(node,tec,size2,year_all3))+nbr_unit_ref(tec))/nbr_unit_ref(tec))**(-b(tec)))]
                                              * [((u(tec,size)/u_ref(tec))**rho(tec))/(u(tec,size)/u_ref(tec))]) ;
INITIAL_YEAR(node,tec,year_all2)$(ord(year_all2) eq 1)..   CAPEX_TEC(node,tec,year_all2) =e= inv_cost_ref(node,tec) ;
NO_BUILT_YEAR(node,tec,year_all2)$(ord(year_all2) gt 1)..   CAPEX_TEC(node,tec,year_all2) =e= bin_cap_new(node,tec,year_all2)*CAPEX_TEC(node,tec,year_all2)
                                                                              + (1-bin_cap_new(node,tec,year_all2))*CAPEX_TEC(node,tec,year_all2-1) ;

model learningeos / all /;
