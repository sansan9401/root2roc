import os,sys,re,json
import ROOT

Flavor=["Muon","Electron"]
Type=["ID","SingleTrigger","DoubleTriggerLeg1","DoubleTriggerLeg2"]
Charge=["Plus","Minus"]
DEBUG=1
def MakeConfig(fname,key=None,isMC=None,iflavor=None,itype=None,icharge=None):
    if DEBUG>1: print("File: "+fname)
    if key==None:
        fin=ROOT.TFile(fname)
        keys=[obj.GetName() for obj in fin.GetListOfKeys()]
        fin.Delete()
        if isMC==0:
            cands=["muonEffi_data_eta_pt","EGamma_EffData2D"]
            for cand in cands:
                if cand in keys:
                    key=cand
                    break
        elif isMC==1:
            cands=["muonEffi_mc_eta_pt","EGamma_EffMC2D"]
            for cand in cands:
                if cand in keys:
                    key=cand
                    break
        else:
            print("[Error] no information about hist key")
            exit(1)
        if key==None:
            print("[Error] Cannot determine key")
            exit(1)
        else:
            if DEBUG>1: print("Key: "+key+" (auto)")
    else:
        if DEBUG>1: print("Key: "+key)

    if isMC==None:
        if "data" in key.lower():
            isMC=0
        elif "mc" in key.lower():
            isMC=1
        if isMC==None:
            print("[Error] Cannot determine whether data or MC")
            exit(1)
        else:
            if DEBUG>1: print("isMC: "+str(bool(isMC))+" (auto)")
    else:
        if DEBUG>1: print("isMC: "+str(bool(isMC)))

    if iflavor==None:
        if "Mu" in fname:
            iflavor=0
        elif "muon" in fname.lower():
            iflavor=0
        elif "Ele" in fname:
            iflavor=1
        elif "egammaEffi" in fname:
            iflavor=1
        if iflavor==None:
            print("[Error] Cannot determine Flavor")
            exit(1)
        else:
            if DEBUG>1: print("Flavor: "+Flavor[iflavor]+" (auto)")
    else:
        if DEBUG>1: print("Flavor: "+Flavor[iflavor])

    if itype==None:
        if not re.search("Mu[0-9]",fname) and not re.search("Ele[0-9][0-9]",fname):
            itype=0
        elif "Leg1" in fname:
            itype=2
        elif "Leg2" in fname:
            itype=3
        elif "Mu17" in fname or "Ele23" in fname:
            itype=2
        elif "Mu8" in fname or "Ele12" in fname:
            itype=3
        else:
            itype=1
        if itype==None:
            print("[Error] Cannot determine Type")
            exit(1)
        else:
            if DEBUG>1: print("Type: "+Type[itype]+" (auto)")
    else:
        if DEBUG>1: print("Type: "+Type[itype])
        
    if icharge==None:
        if "plus" in fname.lower():
            icharge=0
        elif "minus" in fname.lower():
            icharge=1
        if icharge==None:
            print("[Error] Cannot determine Charge")
            exit(1)
        else:
            if DEBUG>1: print("Charge: "+Charge[icharge]+" (auto)")
    else:
        if DEBUG>1: print("Charge: "+Charge[icharge])
        
    return {"file":fname,"key":key,"isMC":isMC,"iflavor":iflavor,"itype":itype,"icharge":icharge}

def root2str(config):
    fname=config["file"]
    key=config["key"]
    isMC=config["isMC"]
    iflavor=config["iflavor"]
    itype=config["itype"]
    icharge=config["icharge"]

    out=["## "+fname+" "+key]

    fin=ROOT.TFile(str(fname))
    hist=fin.Get(str(key))

    etaAxis=hist.GetXaxis()
    ptAxis=hist.GetYaxis()
    
    etaNbins=etaAxis.GetNbins()
    etaBins=[etaAxis.GetBinUpEdge(i) for i in range(etaNbins+1)]
    ptNbins=ptAxis.GetNbins()
    ptBins=[ptAxis.GetBinUpEdge(i) for i in range(ptNbins+1)]
    
    out+=["ETA {flavor} {type} {nbin} {bintype} {bins}".format(flavor=iflavor,type=itype,nbin=etaNbins,bintype=-1,bins=" ".join(map(str,etaBins)))]
    out+=["PT {flavor} {type} {nbin} {bintype} {bins}".format(flavor=iflavor,type=itype,nbin=ptNbins,bintype=-1,bins=" ".join(map(str,ptBins)))]

    for ieta in range(etaNbins):
        effs=[hist.GetBinContent(ieta+1,ipt+1) for ipt in range(ptNbins)]
        out+=["{flavor} 0 0 {isMC} {type} {charge} {ieta} {effs}".format(flavor=iflavor,isMC=int(isMC),type=itype,charge=icharge,ieta=ieta,effs=" ".join(map("{:.3f}".format,effs)))]

    fin.Delete()
    return out


from argparse import ArgumentParser

if __name__ =='__main__':
    parser=ArgumentParser(description="Convert root file efficiency to Rochester txt format")
    parser.add_argument('input',type=str,help="directory containing root files or json file")
    parser.add_argument('output',nargs='?',type=str,default=None,help="output path")
    parser.add_argument('--export-config',dest='config_out',type=str,default=None,help="export config as json format")
    parser.add_argument('--debug',action='store_true',help="debug mode")
    args=parser.parse_args()

    if args.debug: DEBUG=2
    
    configs=[]
    if os.path.isdir(args.input):
        files=os.popen("find "+args.input+" -type f -name *.root").read().split()
        for fname in files:
            configs+=[MakeConfig(fname,isMC=0),MakeConfig(fname,isMC=1)]
        configs=sorted(configs,key=lambda k: k['isMC'])
        configs=sorted(configs,key=lambda k: k['icharge'])
        configs=sorted(configs,key=lambda k: k['itype'])
        configs=sorted(configs,key=lambda k: k['iflavor'])
    elif os.path.isfile(args.input):
        with open(args.input) as f:
            configs=json.load(f)

    lines=[]
    for config in configs:
        lines+=root2str(config)

    if args.output==None:
        args.output=args.input.replace("root/","roc/").strip('/')+".txt"

    if args.config_out:
        with open(args.config_out,"w") as f:
            json.dump(configs,f,indent=2)

    print("------------------------------------ [ "+args.output+" ] -----------------------------------------")
    print("{:9}{:19}{:7}{:6}{:80.79}{:20}".format("Flavor","Type","Charge","isMC","File","Key"))
    for config in configs:
        print("{:9}{:19}{:7}{:6}{:80.79}{:20}".format(Flavor[config["iflavor"]],Type[config["itype"]],Charge[config["icharge"]],str(bool(config["isMC"])),config["file"],config["key"]))
    
    if not os.path.exists(os.path.dirname(os.path.abspath(args.output))):
        os.makedirs(os.path.dirname(args.output))
        
    with open(args.output,"w") as f:
        for line in lines:
            f.write(line+"\n")        

