from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from django.db.models import fields
from django.db import models
import django.forms as forms
from oeplatform import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
# Create your views here.
import matplotlib.pyplot as plt
import urllib3
import json
import datetime
from scipy import stats
import numpy 
import os
from django.conf import settings as djangoSettings
from matplotlib.lines import Line2D
import matplotlib
import time
import re
from .models import Energymodel, Energyframework, Energyscenario, Energystudy
from .forms import EnergymodelForm, EnergyframeworkForm, EnergyscenarioForm, EnergystudyForm
from django.contrib.postgres.fields import ArrayField
import mwclient as mw
import requests

__site = mw.Site(("http", "wiki.openmod-initiative.org"), "/")

def getClasses(sheettype):
    """
    Returns the model and form class w.r.t sheettype.
    """
    if sheettype == "model":
        c = Energymodel
        f = EnergymodelForm
    elif sheettype == "framework":
        c = Energyframework
        f = EnergyframeworkForm
    elif sheettype == "scenario":
        c = Energyscenario
        f = EnergyscenarioForm
    elif sheettype == "studie":
        c = Energystudy
        f = EnergystudyForm
    return c,f



def listsheets(request,sheettype):
    """
    Lists all available model, framework or scenario factsheet objects.
    """
    c,_ = getClasses(sheettype)
    if sheettype == "scenario":
        models = [(m.pk, m.name_of_scenario) for m in c.objects.all()]
    elif sheettype == "studie":
        models = [(m.pk, m.name_of_the_study) for m in c.objects.all()]
    else:
        result = __site.parse('{{#ask: [[Category:Model]]}}')
        print(result)
        models = [r['*'] for r in result['links']]
    return render(request, "modelview/modellist.html", {'models':models})

def ask(query):
    return requests.get('http://wiki.openmod-initiative.org/api.php?format=json&action=ask&query=%s'%query).json()

EM_Map = {
    "model_name" : "Full Model Name",
    "acronym" : "",
    "institutions" : "Author institution",
    "authors" : "Authors",
    "current_contact_person" : "Contact Persons",
    "contact_email" : "Contact Email",
    "website" : "Website",
    "logo" : "Logo",
    "primary_purpose" : "",
    "primary_outputs" : "",
    "support" : "",

    "framework" : "",
    "framework_yes_text" : "",

    "user_documentation" : "",
    "code_documentation" : "",
    "documentation_quality" : "",
    "source_of_funding" : "",
    "open_source" : "Open source licensed",
    "open_up" : "Open future",
    "costs" : "",
    "license" : "License",
    "license_other_text" : "",
    "source_code_available" : "Model source public",
    "gitHub" : "",
    "link_to_source_code" : "",
    "data_provided" : "Data availability",
    "cooperative_programming" : "",
    "number_of_devolopers" : "",
    "number_of_users" : "",
    "modelling_software" : "Modelling software",
    "interal_data_processing_software" : "Processing software",

    "external_optimizer" : "",
    "external_optimizer_yes_text" : "",

    "additional_software" : "",
    "gui" : "",

    "citation_reference" : "Citation references",
    "citation_DOI" : "Citation doi",
    "references_to_reports_produced_using_the_model" : "Report references",
    "larger_scale_usage" : "",

    # Energymodel

    "energy_sectors": "Sectors",
    """
    "energy_sectors_electricity" : "sectors",
    "energy_sectors_heat" : "sectors",
    "energy_sectors_liquid_fuels" : "sectors",
    "energy_sectors_gas" : "sectors",
    "energy_sectors_others" : "sectors",
    "energy_sectors_others_text" : "sectors",
    """

    "demand_sectors" : "",
    """
    "demand_sectors_households" : "",
    "demand_sectors_industry" : "",
    "demand_sectors_commercial_sector" : "",
    "demand_sectors_transport" : "",
    """


    "energy_carrier_gas_natural_gas" : "",
    "energy_carrier_gas_biogas" : "",
    "energy_carrier_gas_hydrogen" : "",

    "energy_carrier_liquids_petrol" : "",
    "energy_carrier_liquids_diesel" : "",
    "energy_carrier_liquids_ethanol" : "",

    "energy_carrier_solid_hard_coal" : "",
    "energy_carrier_solid_hard_lignite" : "",
    "energy_carrier_solid_hard_uranium" : "",
    "energy_carrier_solid_hard_biomass" : "",

    "energy_carrier_renewables_sun" : "",
    "energy_carrier_renewables_wind" : "",
    "energy_carrier_renewables_hydro" : "",
    "energy_carrier_renewables_geothermal_heat" : "",

    "generation": "Technologies",

    """
    "generation_renewables_PV" : "technologies",
    "generation_renewables_wind" : "technologies",
    "generation_renewables_hydro" : "technologies",
    "generation_renewables_biomass" : "technologies",
    "generation_renewables_biogas" : "technologies",
    "generation_renewables_solar_thermal" : "technologies",
    "generation_renewables_others" : "technologies",
    "generation_renewables_others_text" : "",
    "generation_conventional_gas" : "technologies",
    "generation_conventional_coal" : "technologies",
    "generation_conventional_oil" : "technologies",
    "generation_conventional_liquid_fuels" : "technologies",
    "generation_conventional_nuclear" : "technologies",
    "generation_CHP" : "technologies",
    """

    "transfer_electricity" : "",
    "transfer_electricity_distribution" : "",
    "transfer_electricity_transition" : "",

    "transfer_gas" : "",
    "transfer_gas_distribution" : "",
    "transfer_gas_transition" : "",

    "transfer_heat" : "",
    "transfer_heat_distribution" : "",
    "transfer_heat_transition" : "",

    "network_coverage" : "Network coverage",
    """
    "network_coverage_AC" : "network_coverage",
    "network_coverage_DC" : "network_coverage",
    "network_coverage_NT" : "network_coverage",
    """

    "storage_electricity_battery" : "",
    "storage_electricity_kinetic" : "",
    "storage_electricity_CAES" : "",
    "storage_electricity_PHS" : "",
    "storage_electricity_chemical" : "",

    "storage_heat" : "",
    "storage_gas" : "",

    "user_behaviour" : "",
    "user_behaviour_yes_text" : "",
    "changes_in_efficiency" : "",

    "market_models" : "",

    "geographical_coverage" : "Georegions",

    "georesolution" : "Georesolution",

    """geo_resolution_global" : "georesolution",
    "geo_resolution_continents" : "georesolution",
    "geo_resolution_national_states" : "georesolution",
    "geo_resolution_TSO_regions" : "georesolution",
    "geo_resolution_federal_states" : "georesolution",
    "geo_resolution_regions" : "georesolution",
    "geo_resolution_NUTS_3" : "georesolution",
    "geo_resolution_municipalities" : "georesolution",
    "geo_resolution_districts" : "georesolution",
    "geo_resolution_households" : "georesolution",
    "geo_resolution_power_stations" : "georesolution",
    "geo_resolution_others" : "georesolution",
    "geo_resolution_others_text" : """

    "comment_on_geo_resolution" : "",
    "timeresolution": "Timeresolution",

    """
    "time_resolution_anual" : "timeresolution",
    "time_resolution_hour" : "timeresolution",
    "time_resolution_15_min" : "timeresolution",
    "time_resolution_1_min" : "timeresolution",
    """

    "observation_period_more_1_year" : "",
    "observation_period_less_1_year" : "",
    "observation_period_1_year" : "",
    "observation_period_other" : "",
    "observation_period_other_text" : "",

    "time_resolution_other" : "",
    "time_resolution_other_text" : "",

    "additional_dimensions_sector_ecological" : "",
    "additional_dimensions_sector_ecological_text" : "",
    "additional_dimensions_sector_economic" : "",
    "additional_dimensions_sector_economic_text" : "",
    "additional_dimensions_sector_social" : "",
    "additional_dimensions_sector_social_text" : "",
    "additional_dimensions_sector_others" : "",
    "additional_dimensions_sector_others_text" : "",

    "model_class": "Model class",
    """
    "model_class_optimization_LP" : "Model class",
    "model_class_optimization_MILP" : "Model class",
    "model_class_optimization_Nonlinear" : "Model class",
    "model_class_optimization_LP_MILP_Nonlinear_text" : "Model class",

    "model_class_simulation_Agentbased" : "Model class",
    "model_class_simulation_System_Dynamics" : "Model class",
    "model_class_simulation_Accounting_Framework" : "Model class",
    "model_class_simulation_Game_Theoretic_Model" : "Model class",

    "model_class_other" : "",
    "model_class_other_text" : "",
    """


    "short_description_of_mathematical_model_class" : "Math modeltype shortdesc",
    "math_objective": "Math objective",
    """
    "mathematical_objective_cO2" : "Math objective",
    "mathematical_objective_costs" : "Math objective",
    "mathematical_objective_rEshare" : "Math objective",
    "mathematical_objective_other" : "Math objective",
    "mathematical_objective_other_text" : "Math objective",
    """

    "deterministic": "Deterministic",

    """
    "uncertainty_deterministic" : "Deterministic",
    "uncertainty_Stochastic" : "Deterministic",
    "uncertainty_Other" : "",
    "uncertainty_Other_text" : "",
    """
    "montecarlo" : "",

    "typical_computation_time" : "Computation time minutes",

    "typical_computation_hardware" : "",
    "technical_data_anchored_in_the_model" : "",

    "example_research_questions" : "Example research questions",

    "validation_models" : "",
    "validation_measurements" : "",
    "validation_others" : "",
    "validation_others_text" : "",

    "model_specific_properties" : ""
    # Missing: decisions, model_class, number_of_variables, computation_time_comments
    }

def load_EM(name):
    properties = set(EM_Map.values())
    prop_query = "|?".join(properties)
    query = 'http://wiki.openmod-initiative.org/api.php?format=json&action=ask&query=[[Category:Model]]%s'%(prop_query)
    result = requests.get(query).json()

    result = result['query']['results'][name]['printouts']
    m = Energymodel()

    for key in EM_Map:
        if EM_Map[key] in result:
            setattr(m, key, result[EM_Map[key]])
        else:
            print("MISSING: ", key)
            setattr(m, key, None)

    print("unused", [k for k in result if k not in EM_Map.values()])
    return m

def show(request, sheettype, model_name):
    """
    Loads the requested factsheet
    """
    c,_ = getClasses(sheettype)
    #model = get_object_or_404(c, pk=model_name)
    model = load_EM(model_name)
    model_study=[]
    if sheettype == "scenario":
        c_study,_ = getClasses("studie")
        model_study = get_object_or_404(c_study, pk=model.study.pk)
    user_agent = {'user-agent': 'oeplatform'}
    http = urllib3.PoolManager(headers=user_agent)
    org = None
    repo = None
    if sheettype != "scenario" and sheettype !="studie":
        if model.gitHub and model.link_to_source_code:
            try:
                match = re.match(r'.*github\.com\/(?P<org>[^\/]+)\/(?P<repo>[^\/]+)(\/.)*',model.link_to_source_code)
                org = match.group('org')
                repo = match.group('repo')
                gh_url = _handle_github_contributions(org,repo)
            except:
                org = None
                repo = None
    return render(request,("modelview/{0}.html".format(sheettype)),{'model':model,'model_study':model_study,'gh_org':org,'gh_repo':repo})
    

def processPost(post, c, f, files=None, pk=None, key=None):
    """
    Returns the form according to a post request
    """
    fields = {k:post[k] for k in post}
    if 'new' in fields and fields['new']=='True':
        fields['study']=key
    for field in c._meta.get_fields():
        if type(field) == ArrayField:
            parts = []
            for fi in fields.keys():
                if re.match("^{}_\d$".format(field.name),str(fi)) and fields[fi]:
                    parts.append(fi)
            parts.sort()
            fields[field.name]= ",".join(fields[k].replace(",",";") for k in parts)
            for fi in parts:
                del(fields[fi])
        else:
            if field.name in fields:
                fields[field.name] = fields[field.name]
    if pk:
        model = get_object_or_404(c, pk=pk)
        return f(fields,files,instance=model)
    else: 
        return f(fields,files)     
    
    

def editModel(request,model_name, sheettype):
    """
    Constructs a form accoring to existing model
    """
    c,f = getClasses(sheettype) 
        
    model = get_object_or_404(c, pk=model_name)
    form = f(instance=model)
    
    return render(request,"modelview/edit{}.html".format(sheettype),{'form':form, 'name':model_name, 'method':'update'}) 

class FSAdd(View):    
    def get(self,request, sheettype, method='add'):
        c,f = getClasses(sheettype) 
        if method == 'add':
            form = f()
            if sheettype =='scenario':
                c_study,f_study = getClasses('studie')
                formstudy = f_study()
                return render(request,"modelview/new{}.html".format(sheettype),{'form':form, 'formstudy':formstudy, 'method':method})
            else:
                return render(request,"modelview/edit{}.html".format(sheettype),{'form':form, 'method':method})
        else:
            model = get_object_or_404(c, pk=model_name)
            form = f(instance=model)
            return render(request,"modelview/edit{}.html".format(sheettype),{'form':form, 'name':model.pk, 'method':method})
    
    def post(self,request, sheettype, method='add', pk=None):
        c,f = getClasses(sheettype)
        form = processPost(request.POST,  c, f, files=request.FILES, pk=pk)
        if sheettype =='scenario' and method=='add':
            c_study,f_study = getClasses('studie')
            formstudy = processPost(request.POST,  c_study, f_study, files=request.FILES, pk=pk)
            errorsStudy=[]
            print(request.POST['new'])
            if request.POST['new'] == 'True':
                if formstudy.is_valid():
                    n=formstudy.save()
                    form = processPost(request.POST,  c, f, files=request.FILES, pk=pk, key=n.pk)
                else:
                    errorsStudy = [(field.label, str(field.errors.data[0].message)) for field in formstudy if field.errors]
            if form.is_valid() and errorsStudy==[]:
                m = form.save()
                return redirect("/factsheets/{sheettype}s/{model}".format(sheettype=sheettype,model=m.pk))
            else:
                errors = [(field.label, str(field.errors.data[0].message)) for field in form if field.errors]+errorsStudy
                return render(request,"modelview/new{}.html".format(sheettype),{'form':form, 'formstudy':formstudy, 'name':pk, 'method':method, 'errors':errors})
        else:
            if form.is_valid():
                m = form.save()
                return redirect("/factsheets/{sheettype}s/{model}".format(sheettype=sheettype,model=m.pk))
            else:
                errors = [(field.label, str(field.errors.data[0].message)) for field in form if field.errors]
                return render(request,"modelview/edit{}.html".format(sheettype),{'form':form, 'name':pk, 'method':method, 'errors':errors})



def _handle_github_contributions(org,repo, timedelta=3600, weeks_back=8):
    """
    This function returns the url of an image of recent GitHub contributions
    If the image is not present or outdated it will be reconstructed
    """
    path = "GitHub_{0}_{1}_Contribution.png".format(org,repo)
    full_path = os.path.join(djangoSettings.MEDIA_ROOT,path)

    # Is the image already there and actual enough?
    if False:#os.path.exists(full_path) and int(time.time())-os.path.getmtime(full_path) < timedelta:
        return static(path)
    else:
        # We have to replot the image
        # Set plot font
        font = {'family' : 'normal'}
        matplotlib.rc('font', **font)        
        
        # Query GitHub API for contributions
        user_agent = {'user-agent': 'oeplatform'}
        http = urllib3.PoolManager(headers=user_agent)
        try:
            reply = http.request("GET","https://api.github.com/repos/{0}/{1}/stats/commit_activity".format(org,repo)).data.decode('utf8')
        except:
            pass
        
        reply = json.loads(reply)
        
        if not reply:
            return None

        # If there are more weeks than nessecary, truncate
        if weeks_back < len(reply):
            reply = reply[-weeks_back:]
 
        # GitHub API returns a JSON dict with w: weeks, c: contributions
        (times, commits)=zip(*[(datetime.datetime.fromtimestamp(
                int(week['week'])
            ).strftime('%m-%d'), sum(map(int,week["days"]))) for week in reply])
        max_c = max(commits)
        
        # generate a distribution wrt. to the commit numbers
        commits_ids = [i  for i in range(len(commits)) for _ in range(commits[i])]

        # transform the contribution distribution into a density function
        # using a gaussian kernel estimator
        if commits_ids:        
            density = stats.kde.gaussian_kde(commits_ids, bw_method=0.2)
        else:
            # if there are no commits the density is a constant 0
            density = lambda x:0
        # plot this distribution
        x = numpy.arange(0., len(commits),.01)
        c_real_max = max(density(xv) for xv in x) 
        fig1 = plt.figure(figsize=(4, 2))  #facecolor='white',     
        
        # replace labels by dates and numbers of commits
        ax1 = plt.axes(frameon=False)
        plt.fill_between(x, density(x),0)
        ax1.set_frame_on(False)
        ax1.axes.get_xaxis().tick_bottom()
        ax1.axes.get_yaxis().tick_left()
        plt.yticks(numpy.arange(c_real_max-0.001,c_real_max), 
                                [max_c], 
                                size='small')
        plt.xticks(numpy.arange(0.,len(times)), times, size='small',rotation=45)
        
        # save the figure
        plt.savefig(full_path, transparent=True, bbox_inches='tight')
        url = static(path)
        return url
