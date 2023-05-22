SETS
  year           'year'  /1*14/
  size           'size'  / small, medium, large /
  newtec         new technology / wind_ppl /;
ALIAS (size,size2);
ALIAS (year,year2);
PARAMETERS
  cap_new2(newtec,year)        'annual newly installed capacity'
         /         wind_ppl.1        247.65
                   wind_ppl.2        237.95
                   wind_ppl.3        167.65
                   wind_ppl.4        255.25
                   wind_ppl.5        170.7
                   wind_ppl.6        566.2
                   wind_ppl.7        411.95
                   wind_ppl.8        465.5
                   wind_ppl.9        553.65
                   wind_ppl.10        1528.7
                   wind_ppl.11        1757
                   wind_ppl.12        1881.9
                   wind_ppl.13        2961
                   wind_ppl.14        3731 /
  bin_cap_new(newtec,year)     'binary of newly installed capacity'
  rho(newtec)                            'economy of scale parameter'            / wind_ppl      0.91       /
*0.91
  b(newtec)                              'technology cost learning parameter'    / wind_ppl      0.11      /
  u(size)                                'unit size'
         / small      0.04
           medium     0.1
           large      0.5     /
  inv_cost_ref(newtec)              'initial capex'
  nbr_unit_ref(newtec)                   'initial number of unit'                / wind_ppl      4220     /
  u_ref(newtec)                          'reference size'                        / wind_ppl      0.04 / ;
inv_cost_ref(newtec) = 1490 ;
bin_cap_new(newtec,year) = 1;

SCALAR hist_length                       the length of historical periods;
hist_length = card(year);

VARIABLES
  NBR_UNIT(newtec,size,year)   number of units for each size every year
  CAPEX_TEC(newtec,year)       capital cost in dollar per kW
  OBJECT                                 objective function ;

POSITIVE VARIABLES
  NBR_UNIT ;

EQUATIONS
  OBJECTIVE_INNER        total investment cost
  CAP_NEW_BALANCE        installed capacity balance
  CAPEX_ESTIMATE         estimating average capex
  NO_BUILT_YEAR          annual investment cost
;


OBJECTIVE_INNER..                        OBJECT =e= sum((newtec,year), CAPEX_TEC(newtec,year)*cap_new2(newtec,year)) ;
CAP_NEW_BALANCE(newtec,year).. sum(size, NBR_UNIT(newtec,size,year)*u(size)) =e= cap_new2(newtec,year) ;
CAPEX_ESTIMATE(newtec,year)..  CAPEX_TEC(newtec,year)*cap_new2(newtec,year) =g= sum(size,inv_cost_ref(newtec)
                                              * NBR_UNIT(newtec,size,year)*u(size)
                                              * [(((sum((size2,year2)$(ord(year2) le ord(year)-1), NBR_UNIT(newtec,size2,year2))+nbr_unit_ref(newtec))/nbr_unit_ref(newtec))**(-b(newtec)))]
                                              * [((u(size)/u_ref(newtec))**rho(newtec))/(u(size)/u_ref(newtec))]) ;
NO_BUILT_YEAR(newtec,year)..   CAPEX_TEC(newtec,year) =e= bin_cap_new(newtec,year)*CAPEX_TEC(newtec,year)
                                                                              + (1-bin_cap_new(newtec,year))*CAPEX_TEC(newtec,year-1) ;

model learningeos / all /;
solve learningeos using nlp minimizing OBJECT;

PARAMETERS
new_cap_by_size(newtec,size,year) new capacity by size;

new_cap_by_size(newtec,size,year) = NBR_UNIT.l(newtec,size,year)*u(size);

Execute_Unload "Learning_dummy.gdx";
