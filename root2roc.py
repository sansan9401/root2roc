import os,sys,re,json,random
import ROOT

Flavor=["Muon","Electron"]
Type=["RECO","ID","SLT1","SLT2","DLTLeg1","DLTLeg2","SelQ_ID","SelQ_SLT1","SelQ_SLT2","DLTDZ","Tracking"]
Charge=["Plus","Minus","Inclusive"]
DEBUG=1
NREPLICA=100

def GetListOfKeys(fname):
    fin=ROOT.TFile(fname)
    keys=[obj.GetName() for obj in fin.GetListOfKeys()]
    fin.Delete()
    return keys

def IsUniformBins(axis):
    if axis is None: return None
    width=None
    for i in range(1,axis.GetNbins()+1):
        if width is None: width=axis.GetBinWidth(i)
        if abs((axis.GetBinWidth(i)-width)/width)>0.0001:
            return False
    return True

def MakeConfig(fname,key=None,isMC=None,iflavor=None,itype=None,icharge=None,iset=None,imem=None,option=""):
    if DEBUG>1: print("File: "+fname)
    ref=None
    ref_cands=[]
    if key==None:
        if isMC==0:
            key="data"
        elif isMC==1:
            key="sim"
        else:
            print("[Warning] Cannot determine key")
            return None
            
        if iset>1:
            key+="_s{}m{}".format(iset-2,imem)
            
        if DEBUG>1: print("Key: "+key+" (auto)")
    else:
        if DEBUG>1: print("Key: "+key)

    if isMC==None:
        if "data" in key.lower():
            isMC=0
        elif "sim" in key.lower():
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
        if "RECO" in fname or "StandAloneMuon" in fname or "TrackerMuon" in fname:
            itype=0
        elif "GlobalMuon" in fname:
            itype=10
        elif "DZ" in fname:
            itype=9
        elif not re.search("Mu[0-9]",fname) and not re.search("Ele[0-9][0-9]",fname):
            if "SelQ" not in fname:
                itype=1
            else:
                itype=6
        elif "Leg1" in fname:
            itype=4
        elif "Leg2" in fname:
            itype=5
        elif "Mu17" in fname or "Ele23" in fname:
            itype=4
        elif "Mu8" in fname or "Ele12" in fname:
            itype=5
        elif "Ele27_" in fname or "Ele28_" in fname:
            if "SelQ" not in fname:
                itype=2
            else:
                itype=7
        elif "Mu24_" in fname:
            itype=2
        elif "Ele32_" in fname:
            if "SelQ" not in fname:
                itype=3
            else:
                itype=8
        elif "Mu27_" in fname:
            itype=3

        if itype==None:
            print("[Warning] Cannot determine Type of {}".format(fname))
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
        else:
            icharge=2
        if icharge==None:
            print("[Warning] Cannot determine Charge")
            return None
        else:
            if DEBUG>1: print("Charge: "+Charge[icharge]+" (auto)")
    else:
        if DEBUG>1: print("Charge: "+Charge[icharge])

    if iset==None:
        if key in ["data","sim"]:
            iset=0
        elif "_s0m0" in key and "err" in option:
            iset=1
        elif re.search('_s([0-9]*)m',key):
            iset=int(re.search('_s([0-9]*)m',key).group(1))+2
        if iset==None:
            print("[Warning] Cannot determine iset")
            return None
        else:
            if DEBUG>1: print("iset: "+str(iset)+" (auto)")
    else:
        if DEBUG>1: print("iset: "+str(iset))

    if imem==None:
        if key in ["data","sim"]:
            imem=0
        elif "replica" in option:
            imem=NREPLICA
        elif re.search('_s[0-9]*m([0-9]*)',key):
            imem=int(re.search('_s[0-9]*m([0-9]*)',key).group(1))
        if imem==None:
            print("[Warning] Cannot determine imem")
            return None
        else:
            if DEBUG>1: print("imem: "+str(imem)+" (auto)")
    else:
        if DEBUG>1: print("imem: "+str(imem))
        
    if "dummy" in option or "ones" in option:
        key=key.split("_")[0]

    return {"file":fname,"key":key,"isMC":isMC,"iflavor":iflavor,"itype":itype,"icharge":icharge,"iset":iset,"imem":imem,"ref":ref,"option":option}

def root2str(config):
    fname=config["file"]
    key=config["key"]
    isMC=config["isMC"]
    iflavor=config["iflavor"]
    itype=config["itype"]
    icharge=config["icharge"]
    iset=config["iset"]
    imem=config["imem"]
    option=config["option"]

    out=["## "+fname+" "+key+" "+option]
    if "replica" in option and imem>=NREPLICA:
        for i in range(NREPLICA):
            c=config.copy()
            c["imem"]=i
            out+=root2str(c)        
    else:
        fin=ROOT.TFile(str(fname))
        hist=fin.Get(str(key))
        if "ones" in option:
            for i in range(hist.GetNcells()):
                hist.SetBinContent(i,1)
                hist.SetBinError(i,0)

        etaAxis=hist.GetXaxis()
        ptAxis=hist.GetYaxis()
    
        etaNbins=etaAxis.GetNbins()
        ptNbins=ptAxis.GetNbins()

        if IsUniformBins(etaAxis):
            out+=["ETA {flavor} {type} {nbin} {binwidth} {lowedge}".format(flavor=iflavor,type=itype,nbin=etaNbins,binwidth=round(etaAxis.GetBinWidth(1),4),lowedge=etaAxis.GetBinLowEdge(1))]
        else:
            etaBins=[round(etaAxis.GetBinUpEdge(i),4) for i in range(etaNbins+1)]
            out+=["ETA {flavor} {type} {nbin} {bintype} {bins}".format(flavor=iflavor,type=itype,nbin=etaNbins,bintype=-1,bins=" ".join(map(str,etaBins)))]            

        if IsUniformBins(ptAxis):
            out+=["PT {flavor} {type} {nbin} {binwidth} {lowedge}".format(flavor=iflavor,type=itype,nbin=ptNbins,binwidth=ptAxis.GetBinWidth(1),lowedge=ptAxis.GetBinLowEdge(1))]
        else:
            ptBins=[ptAxis.GetBinUpEdge(i) for i in range(ptNbins+1)]
            out+=["PT {flavor} {type} {nbin} {bintype} {bins}".format(flavor=iflavor,type=itype,nbin=ptNbins,bintype=-1,bins=" ".join(map(str,ptBins)))]

        if "replica" in option:
            random.seed(hash(config["file"]+config["key"]+str(config["imem"])))
            hist_ref=fin.Get(config["ref"])
            contentIsError=False
            if hist_ref:
                for i in range(hist_ref.GetNcells()):
                    if hist.GetBinContent(i)!=hist_ref.GetBinContent(i): contentIsError=True
        for ieta in range(etaNbins):
            if "replica" in option:
                if contentIsError:
                    effs=[random.gauss(hist_ref.GetBinContent(ieta+1,ipt+1),hist.GetBinContent(ieta+1,ipt+1)) for ipt in range(ptNbins)]
                else:
                    effs=[random.gauss(hist.GetBinContent(ieta+1,ipt+1),hist.GetBinError(ieta+1,ipt+1)) for ipt in range(ptNbins)]
            elif "err" in option:    
                effs=[hist.GetBinError(ieta+1,ipt+1) for ipt in range(ptNbins)]
            else:
                effs=[hist.GetBinContent(ieta+1,ipt+1) for ipt in range(ptNbins)]
                
            effs=[max(0,min(1,eff)) for eff in effs]
            out+=["{flavor} {set} {mem} {isMC} {type} {charge} {ieta} {effs}".format(flavor=iflavor,set=iset,mem=imem,isMC=int(isMC),type=itype,charge=icharge,ieta=ieta,effs=" ".join(map("{:.5f}".format,effs)))]
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
            keys=[key for key in GetListOfKeys(fname) if "_sys" not in key and "sf" not in key]                
            for key in keys:
                if "_s0m0" in key:
                    c=MakeConfig(fname,key,option="err")
                    if c: configs+=[c]
                    #c=MakeConfig(fname,key,option="replica")
                    #if c: configs+=[c]
                else:
                    c=MakeConfig(fname,key)
                    if c: configs+=[c]
            ##FIXME: for temporal add dummy set
            #print keys
            if "Electron" in args.input:
                for sample in ["data","sim"]:
                    for (i,j) in [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(7,1),(8,0),(8,1),(9,0),(10,0),(11,0),(11,1),(12,0),(12,1),(13,0),(13,1),(14,0),(15,0),(16,0),(17,0),(18,0)]:
                        key="{}_s{}m{}".format(sample,i,j)
                        if key not in keys:
                            c=MakeConfig(fname,key,option="dummy")
                            if c: configs+=[c]
            if "Muon" in args.input:
                for sample in ["data","sim"]:
                    for (i,j) in [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(7,1),(8,0),(8,1),(9,0),(10,0),(11,0),(11,1),(12,0),(12,1),(13,0),(13,1),(14,0),(15,0),(16,0),(17,0),(18,0)]:
                        key="{}_s{}m{}".format(sample,i,j)
                        if key not in keys:
                            if i==17 and j==0 and "TrackerMuonOrGlobalMuon" in fname:
                                c=MakeConfig(fname,key,option="ones")
                            else:
                                c=MakeConfig(fname,key,option="dummy")
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
               and configs[i]["itype"]==configs[j]["itype"] and configs[i]["icharge"]==configs[j]["icharge"] \
               and configs[i]["option"]==configs[j]["option"]:
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
        nmem+=[max([c["imem"] if "replica" not in c["option"] else NREPLICA-1 for c in configs if c["iset"]==iset]+[-1])+1]
    lines+=["NMEM "+" ".join([str(i) for i in nmem])]
    for config in configs:
        lines+=root2str(config)

    if args.output==None:
        args.output=args.input.replace("root/","roc/").strip('/')+".txt"

    print("------------------------------------ [ "+args.output+" ] -----------------------------------------")
    print("{:9}{:4}{:5}{:7}{:15}{:12}{:80.79}{:20}{:10}".format("Flavor","Set","Mem","isMC","Type","Charge","File","Key","Option"))
    for config in configs:
        print("{:9}{:<4}{:<5}{:7}{:15}{:12}{:80.79}{:20}{:10}".format(
            Flavor[config["iflavor"]],
            config["iset"],
            config["imem"],
            str(config["isMC"])+":"+("MC" if config["isMC"] else "data"),
            str(config["itype"])+":"+Type[config["itype"]],
            str(config["icharge"])+":"+Charge[config["icharge"]],
            config["file"],
            config["key"],
            config["option"],
        ))
    
    if not os.path.exists(os.path.dirname(os.path.abspath(args.output))):
        os.makedirs(os.path.dirname(args.output))
        
    with open(args.output,"w") as f:
        for line in lines:
            f.write(line+"\n")        

