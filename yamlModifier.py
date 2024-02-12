import yaml
import io
import glob

def yamlLoader(fname):
    with open(f"{fname}", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
def yamlModifier(fnames):
    data = yamlLoader(fnames)
    
    ## Load in the relevant data
    tx_sync_word = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['tx_sync_word']['value']
    buff_t1 = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['buff_t1']['value']
    buff_t2 = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['buff_t2']['value']
    buff_t3 = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['buff_t3']['value']
    active_etxs = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['config']['params']['eporttx_numen']['param_value']
    stc_type = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['config']['params']['stc_type']['param_value']
    use_sum = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['config']['params']['use_sum']['param_value']
    Mux = data['ECON-T']['RW']['MFC_MUX_SELECT']['registers']['mux_select_*']['value']
    Cal = data['ECON-T']['RW']['MFC_CAL_VAL']['registers']['cal_*']['value']
    select = data['ECON-T']['RW']['MFC_ALGORITHM_SEL_DENSITY']['registers']['algo']['params']['select']['param_value']
    density = data['ECON-T']['RW']['MFC_ALGORITHM_SEL_DENSITY']['registers']['algo']['params']['density']['param_value']
    if 'ALGO_THRESHOLD_VAL' in data['ECON-T']['RW'].keys():
        AlgoThreshold = data['ECON-T']['RW']['ALGO_THRESHOLD_VAL']['registers']['threshold_val_*']['value']
    AlgoDroplsb = data['ECON-T']['RW']['ALGO_DROPLSB']['registers']['drop_lsb']['value']
    if 'ALGO_THRESHOLD_VAL' in data['ECON-T']['RW'].keys():
        ## Construct the new YAML File 
        new_file = {'FormatterBuffer': {'Global': {
                                            'tx_sync_word': tx_sync_word,
                                            'buff_t1': buff_t1,
                                            'buff_t2': buff_t2,
                                            'buff_t3': buff_t3,
                                            'active_etxs': active_etxs,
                                            'stc_type': stc_type,
                                            'use_sum': use_sum,}},
                   'Mux':{
                       i: Mux[i] for i in range(len(Mux))},
                   'Cal':{i: Cal[i] for i in range(len(Cal))},
                   'Algorithm':{'Global':{
                                   'select': select,
                                   'density': density,
                   }},
                   'AlgoThreshold':{i:AlgoThreshold[i] for i in range(len(AlgoThreshold))},
                   'AlgoDroplsb':{'Global': AlgoDroplsb}}
    else:
        ## Construct the new YAML File 
        new_file = {'FormatterBuffer': {'Global': {
                                            'tx_sync_word': tx_sync_word,
                                            'buff_t1': buff_t1,
                                            'buff_t2': buff_t2,
                                            'buff_t3': buff_t3,
                                            'active_etxs': active_etxs,
                                            'stc_type': stc_type,
                                            'use_sum': use_sum,}},
                   'Mux':{
                       i: Mux[i] for i in range(len(Mux))},
                   'Cal':{i: Cal[i] for i in range(len(Cal))},
                   'Algorithm':{'Global':{
                                   'select': select,
                                   'density': density,
                   }},
                    'AlgoDroplsb':{'Global': AlgoDroplsb}}
    outdir = fnames.split('init.yaml')[0]

    # Write YAML file
    with io.open(f'{outdir}/init.yaml', 'w', encoding='utf8') as outfile:
        yaml.dump(new_file, outfile, default_flow_style=False, allow_unicode=True)

list_of_files_in_directories = glob.glob("**/init.yaml",recursive=True)

for files in list_of_files_in_directories:
    try:
        yamlModifier(files)
    except:
        print("error:",files)

