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
    weights = [0,16, 32, 48,64, 80,96,112,128]
    ## Load in the relevant data
    mask_ae = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['mask_ae']['value']
    mask_ae2 = data['ECON-T']['RW']['FMTBUF_ALL']['registers']['mask_ae2']['value']
    Mux = data['ECON-T']['RW']['MFC_MUX_SELECT']['registers']['mux_select_*']['value']
    Cal = data['ECON-T']['RW']['MFC_CAL_VAL']['registers']['cal_*']['value']
    select = data['ECON-T']['RW']['MFC_ALGORITHM_SEL_DENSITY']['registers']['algo']['params']['sele\
ct']['param_value']
    density = data['ECON-T']['RW']['MFC_ALGORITHM_SEL_DENSITY']['registers']['algo']['params']['den\
sity']['param_value']
    
    ## Construct the new YAML File 
    new_file = {'FormatterBuffer': {'Global': {
                                        'mask_ae': mask_ae,
                                        'mask_ae2': mask_ae2,}},
               'Mux':{
                   i: Mux[i] for i in range(len(Mux))},
               'Cal':{i: Cal[i] for i in range(len(Cal))},
                'Algorithm':{'Global':{
                                   'select': select,
                                   'density': density,
                   }},
                'Encoder':{i: {f'weights_byte{weight}': data['ECON-T']['RW'][f'AUTOENCODER_{i}INPUT']['registers'][f'weights_byte{weight}']['value'] for weight in weights} for i in range (12)}
               }
    print(new_file)
    # Write YAML file
    with io.open(f'./init.yaml', 'w', encoding='utf8') as outfile:
        yaml.dump(new_file, outfile, default_flow_style=False, allow_unicode=True)

yamlModifier('./init.yaml')
