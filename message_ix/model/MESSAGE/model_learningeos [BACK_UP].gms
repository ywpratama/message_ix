
PARAMETERS
* inherrited parameters
  cap_new2(newtec,year_all2)             'annual newly installed capacity'
  bin_cap_new(newtec,year_all2)          'binary of newly installed capacity'

* learning and economies of scale parameters
  alpha(newtec)                          'technology cost learning parameter'
  beta_unit(newtec)                      'economy of scale parameter at unit level'
  beta_proj(newtec)                      'economy of scale parameter at project level'
  gamma_unit(newtec)                     'unit scale-up rate'
  gamma_proj(newtec)                     'project scale-up rate'

* initial condition
  inv_cost_refidx(newtec)                'initial capex'
  knref_unit(newtec)                     'initial number of unit'
  sizeref_unit(newtec)                   'initial size of unit'
  sizeref_proj(newtec)                   'initial size of project'

* log2 parameters
  log2_cap_new2(newtec,year_all2)        'log2 of new capacity addition'
  log2_inv_cost_refidx(newtec)           'log2 of initial capex'
  log2_knref_unit(newtec)                'log2 of initial number of unit'
  log2_sizeref_unit(newtec)              'log2 of initial size of unit'
  log2_sizeref_proj(newtec)              'log2 of initial size of project'
;


log2_inv_cost_refidx(newtec)    = log2(inv_cost_refidx(newtec)) ;
log2_knref_unit(newtec)         = log2(knref_unit(newtec)) ;
log2_sizeref_unit(newtec)       = log2(sizeref_unit(newtec)) ;
log2_sizeref_proj(newtec)       = log2(sizeref_proj(newtec)) ;


SCALAR hist_length                       'the length of historical periods' ;
hist_length = card(year_all2) - card(model_horizon);

VARIABLES
  LOG2_IC(newtec,year_all2)              'capital cost in dollar per kW'
  LOG2_N_UNIT(newtec,year_all2)          'number of new units for each size every year'
  LOG2_KN_UNIT(newtec,year_all2)         'number of cumulative units for each size every year'
  LOG2_S_UNIT(newtec,year_all2)          'number of units for each size every year'
  LOG2_S_PROJ(newtec,year_all2)          'number of units for each size every year'
  LOG2_1pC_UNIT(newtec,year_all2)        'number of units for each size every year'
  LOG2_1pC_PROJ(newtec,year_all2)        'number of units for each size every year'
  IC(newtec,year_all2)                   'capital cost in dollar per kW'
  OBJECT                                 'objective function'
;

POSITIVE VARIABLES LOG2_1pC_UNIT, LOG2_1pC_PROJ;

EQUATIONS
  OBJECTIVE_INNER                        'total investment cost'
  CAP_NEW_BALANCE                        'installed capacity balance'
  CAPEX_ESTIMATE                         'estimating average capex'
  CUMUL_UNIT_INI                         'cumulative units'
  CUMUL_UNIT                             'cumulative units'
  UNIT_SCALEUP_LIM_INI                   'unit scale-up limit'
  UNIT_SCALEUP_LIM                       'unit scale-up limit'
  PROJ_SCALEUP_LIM_INI                   'project scale-up limit'
  PROJ_SCALEUP_LIM                       'project scale-up limit'
  NO_BUILT_YEAR                          'annual investment cost'
  UNIT_SIZELB                            'unit size temporary constraint'
  PROJ_SIZELB                            'project size temporary constraint'
;


OBJECTIVE_INNER..        OBJECT =e= sum((node,newtec,year_all2),
                         IC(newtec,year_all2) * cap_new2(newtec,year_all2)) ;

CAP_NEW_BALANCE(node,newtec,year_all2)..
         log2_cap_new2(newtec,year_all2) * bin_cap_new(newtec,year_all2) =e=
         LOG2_N_UNIT(newtec,year_all2) + LOG2_S_UNIT(newtec,year_all2) ;

CAPEX_ESTIMATE(node,newtec,year_all2)..  LOG2_IC(newtec,year_all2) =e=
         LOG2_IC(newtec,year_all2-1)
         - alpha(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - LOG2_KN_UNIT(newtec,year_all2-1)] * bin_cap_new(newtec,year_all2)
         - beta_unit(newtec) * [LOG2_S_UNIT(newtec,year_all2) - LOG2_S_UNIT(newtec,year_all2-1)] * bin_cap_new(newtec,year_all2)
         - beta_proj(newtec) * [LOG2_S_PROJ(newtec,year_all2) - LOG2_S_PROJ(newtec,year_all2-1)] * bin_cap_new(newtec,year_all2)
         + beta_unit(newtec) * LOG2_1pC_UNIT(newtec,year_all2) * bin_cap_new(newtec,year_all2)
         + beta_proj(newtec) * LOG2_1pC_PROJ(newtec,year_all2) * bin_cap_new(newtec,year_all2) ;

CUMUL_UNIT_INI(newtec,year_all2)$(ord(year_all2) le (hist_length+1))..
         2**LOG2_KN_UNIT(newtec,year_all2) =e=
         2**log2_knref_unit(newtec)
         + (2**LOG2_N_UNIT(newtec,year_all2)) * bin_cap_new(newtec,year_all2) ;

CUMUL_UNIT(newtec,year_all2)$(ord(year_all2) gt (hist_length+1))..
         2**LOG2_KN_UNIT(newtec,year_all2) =e=
         2**LOG2_KN_UNIT(newtec,year_all2-1)
         + (2**LOG2_N_UNIT(newtec,year_all2)) * bin_cap_new(newtec,year_all2) ;

UNIT_SCALEUP_LIM_INI(newtec,year_all2)$(ord(year_all2) le (hist_length+1))..
         LOG2_S_UNIT(newtec,year_all2) - LOG2_1pC_UNIT(newtec,year_all2) =l=
         log2[ 2**log2_sizeref_unit(newtec)
               + gamma_unit(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - log2_knref_unit(newtec)] ] ;

UNIT_SCALEUP_LIM(newtec,year_all2)$(ord(year_all2) gt (hist_length+1))..
         LOG2_S_UNIT(newtec,year_all2) - LOG2_1pC_UNIT(newtec,year_all2) =l=
         log2[ 2**LOG2_S_UNIT(newtec,year_all2-1)
               + gamma_unit(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - LOG2_KN_UNIT(newtec,year_all2-1)] ] ;

PROJ_SCALEUP_LIM_INI(newtec,year_all2)$(ord(year_all2) le (hist_length+1))..
         LOG2_S_PROJ(newtec,year_all2) - LOG2_1pC_PROJ(newtec,year_all2) =l=
         log2[ 2**log2_sizeref_proj(newtec)
               + gamma_proj(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - log2_knref_unit(newtec)] ] ;

PROJ_SCALEUP_LIM(newtec,year_all2)$(ord(year_all2) gt (hist_length+1))..
         LOG2_S_PROJ(newtec,year_all2) - LOG2_1pC_PROJ(newtec,year_all2) =l=
         log2[ 2**LOG2_S_PROJ(newtec,year_all2-1)
               + gamma_proj(newtec) * [LOG2_KN_UNIT(newtec,year_all2) - LOG2_KN_UNIT(newtec,year_all2-1)] ] ;

NO_BUILT_YEAR(newtec,year_all2)..
         IC(newtec,year_all2) =e=
         bin_cap_new(newtec,year_all2) * 2**LOG2_IC(newtec,year_all2)
         + (1-bin_cap_new(newtec,year_all2)) * IC(newtec,year_all2-1) ;


UNIT_SIZELB(newtec,year_all2)..
         LOG2_S_UNIT(newtec,year_all2) =g=
         log2_sizeref_unit(newtec) ;

PROJ_SIZELB(newtec,year_all2)..
         LOG2_S_PROJ(newtec,year_all2) =g=
         log2_sizeref_proj(newtec) ;


model learningeos / all /;
