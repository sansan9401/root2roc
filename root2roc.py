import os,sys,re,json,random
import ROOT

Flavor=["Muon","Electron"]
Type=["ID","SingleTrigger","DoubleTriggerLeg1","DoubleTriggerLeg2","SingleTrigger1","SingleTrigger2","RECO"]
Charge=["Plus","Minus"]
DEBUG=1
NREPLICA=100
def MakeConfig(fname,key=None,isMC=None,iflavor=None,itype=None,icharge=None,iset=0,imem=0):
    if DEBUG>1: print("File: "+fname)
    ref=None
    ref_cands=[]
    if key==None:
        fin=ROOT.TFile(fname)
        keys=[obj.GetName() for obj in fin.GetListOfKeys()]
        fin.Delete()
        if isMC==0:
            if iset==0: 
                cands=["muonEffi_data_eta_pt","EGamma_EffData2D"]
            elif iset==1: 
                cands=["EGamma_EffData2D_stat","statData"]
                ref_cands=["muonEffi_data_eta_pt","EGamma_EffData2D"]
                imem=None
            elif iset==2:
                cands=["EGamma_EffData2D_altBkg","altBkgModel"]
            elif iset==3:
                cands=["EGamma_EffData2D_altSig","altSignalModel"]
            elif iset==4:
                cands=["EGamma_EffData2D"]
            elif iset==5:
                cands=["EGamma_EffData2D"]
        elif isMC==1:
            if iset==0:
                cands=["muonEffi_mc_eta_pt","EGamma_EffMC2D"]
            elif iset==1: 
                cands=["EGamma_EffMC2D_stat","statMC"]
                ref_cands=["muonEffi_mc_eta_pt","EGamma_EffMC2D"]
                imem=None
            elif iset==2:
                cands=["EGamma_EffMC2D"]
            elif iset==3:
                cands=["EGamma_EffMC2D"]
            elif iset==4:
                cands=["EGamma_EffMC2D_altMC","altMCEff"]
            elif iset==5:
                cands=["EGamma_EffMC2D_altTag","altTagSelection"]
                
        else:
            print("[Warning] no information about hist key")
            return None
        for cand in cands:
            if cand in keys:
                key=cand
                break
        for cand in ref_cands:
            if cand in keys:
                ref=cand
                break
        if key==None:
            print("[Warning] Cannot determine key")
            return None
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
            print("[Warning] Cannot determine whether data or MC")
            return None
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
            print("[Warning] Cannot determine Flavor")
            return None
        else:
            if DEBUG>1: print("Flavor: "+Flavor[iflavor]+" (auto)")
    else:
        if DEBUG>1: print("Flavor: "+Flavor[iflavor])

    if itype==None:
        if "egammaEffi_ptAbove20" in fname:
            itype=6
        elif not re.search("Mu[0-9]",fname) and not re.search("Ele[0-9][0-9]",fname):
            itype=0
        elif "Leg1" in fname:
            itype=2
        elif "Leg2" in fname:
            itype=3
        elif "Mu17" in fname or "Ele23" in fname:
            itype=2
        elif "Mu8" in fname or "Ele12" in fname:
            itype=3
        elif "2017" in fname and "Ele27_" in fname:
            itype=4
        elif "2017" in fname and "Mu24_" in fname:
            itype=4
        elif "2018" in fname and "Ele28_" in fname:
            itype=4
        elif "2017" in fname and "Ele32_" in fname:
            itype=5
        elif "2017" in fname and "Mu27_" in fname:
            itype=5
        elif "2018" in fname and "Ele32_" in fname:
            itype=5
        else:
            itype=1
        if itype==None:
            print("[Warning] Cannot determine Type")
            return None
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
            print("[Warning] Cannot determine Charge")
            return None
        else:
            if DEBUG>1: print("Charge: "+Charge[icharge]+" (auto)")
    else:
        if DEBUG>1: print("Charge: "+Charge[icharge])
        
    return {"file":fname,"key":key,"isMC":isMC,"iflavor":iflavor,"itype":itype,"icharge":icharge,"iset":iset,"imem":imem,"ref":ref}

def root2str(config):
    fname=config["file"]
    key=config["key"]
    isMC=config["isMC"]
    iflavor=config["iflavor"]
    itype=config["itype"]
    icharge=config["icharge"]
    iset=config["iset"]
    imem=config["imem"]

    out=["## "+fname+" "+key]
    if iset==1 and imem==None:
        for i in range(NREPLICA):
            c=config.copy()
            c["imem"]=i
            out+=root2str(c)
    else:
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

        if iset==1:
            random.seed(hash(config["file"]+config["key"]+str(config["imem"])))
            hist_ref=fin.Get(config["ref"])
            contentIsError=False
            for i in range(hist_ref.GetNcells()):
                if hist.GetBinContent(i)!=hist_ref.GetBinContent(i): contentIsError=True
        for ieta in range(etaNbins):
            if iset==1:
                if contentIsError:
                    effs=[random.gauss(hist_ref.GetBinContent(ieta+1,ipt+1),hist.GetBinContent(ieta+1,ipt+1)) for ipt in range(ptNbins)]
                else:
                    effs=[random.gauss(hist.GetBinContent(ieta+1,ipt+1),hist.GetBinError(ieta+1,ipt+1)) for ipt in range(ptNbins)]
            else: 
                effs=[hist.GetBinContent(ieta+1,ipt+1) for ipt in range(ptNbins)]
            effs=[max(0,min(1,eff)) for eff in effs]
            out+=["{flavor} {set} {mem} {isMC} {type} {charge} {ieta} {effs}".format(flavor=iflavor,set=iset,mem=imem,isMC=int(isMC),type=itype,charge=icharge,ieta=ieta,effs=" ".join(map("{:.3f}".format,effs)))]
            if any(x>1 for x in effs):
                print("[Warning] efficiency larger than 1")
                print(out[-1])

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
            for isMC in [0,1]:
                for iset in [0,1,2,3,4,5]:
                    if "egammaEffi_ptAbove20" in fname:
                        c=MakeConfig(fname,isMC=isMC,iset=iset,icharge=0)
                        if c: configs+=[c]
                        c=MakeConfig(fname,isMC=isMC,iset=iset,icharge=1)
                        if c: configs+=[c]
                    else:
                        c=MakeConfig(fname,isMC=isMC,iset=iset)
                        if c: configs+=[c]
        configs=sorted(configs,key=lambda k: k['isMC'])
        configs=sorted(configs,key=lambda k: k['icharge'])
        configs=sorted(configs,key=lambda k: k['itype'])
        configs=sorted(configs,key=lambda k: k['iflavor'])
        configs=sorted(configs,key=lambda k: k['iset'])
    elif os.path.isfile(args.input):
        with open(args.input) as f:
            configs=json.load(f)

    ### Check duplicates
    for i in range(len(configs)):
        for j in range(i+1,len(configs)):
            if configs[i]["iflavor"]==configs[j]["iflavor"] and configs[i]["iset"]==configs[j]["iset"] \
               and configs[i]["imem"]==configs[j]["imem"] and configs[i]["isMC"]==configs[j]["isMC"] \
               and configs[i]["itype"]==configs[j]["itype"] and configs[i]["icharge"]==configs[j]["icharge"]:
                print("[Error] duplicated configs")
                print(configs[i])
                print(configs[j])
                args.config_out="duplicate.json"

    if args.config_out:
        with open(args.config_out,"w") as f:
            json.dump(configs,f,indent=2)
            exit(0)

    lines=[]
    nset=max([c["iset"] for c in configs])+1
    lines+=["NSET "+str(nset)]
    nmem=[]
    for iset in range(nset):
        nmem+=[max([c["imem"] if c["imem"]!=None else NREPLICA-1 for c in configs if c["iset"]==iset])+1]
    lines+=["NMEM "+" ".join([str(i) for i in nmem])]
    for config in configs:
        lines+=root2str(config)

    if args.output==None:
        args.output=args.input.replace("root/","roc/").strip('/')+".txt"

    print("------------------------------------ [ "+args.output+" ] -----------------------------------------")
    print("{:9}{:4}{:7}{:6}{:19}{:7}{:80.79}{:20}".format("Flavor","Set","Member","isMC","Type","Charge","File","Key"))
    for config in configs:
        print("{:9}{:<4}{:<7}{:6}{:19}{:7}{:80.79}{:20}".format(Flavor[config["iflavor"]],config["iset"],config["imem"],str(bool(config["isMC"])),Type[config["itype"]],Charge[config["icharge"]],config["file"],config["key"]))
    
    if not os.path.exists(os.path.dirname(os.path.abspath(args.output))):
        os.makedirs(os.path.dirname(args.output))
        
    with open(args.output,"w") as f:
        for line in lines:
            f.write(line+"\n")        

