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


FW_Map = {
    "model_name" : "Full Model Name",
    "acronym" : "",
    "institutions" : "Author institution",
    "authors" : "Authors",
    "current_contact_person" : "Contact Persons",
    "contact_email" : "Contact Email",
    "website" : "Website",
    "logo" : "Logo",
    "primary_purpose" : "Primary purpose",
    "primary_outputs" : "Primary outpurs",
    "support" : "Support",

    "framework" : "",
    "framework_yes_text" : "",

    "user_documentation" : "User documentation",
    "code_documentation" : "Code documentation",
    "documentation_quality" : "",
    "source_of_funding" : "Source of funcing",
    "open_source" : "Open source licensed",
    "open_up" : "Open future",
    "costs" : "",
    "license" : "License",
    "license_other_text" : "",
    "source_code_available" : "Model source public",
    "gitHub" : "",
    "link_to_source_code" : "Link to source",
    "data_provided" : "Data availability",
    "cooperative_programming" : "",
    "number_of_devolopers" : "Number of developers",
    "number_of_users" : "Number of users",
    "modelling_software" : "Modelling software",
    "interal_data_processing_software" : "Processing software",

    "external_optimizer" : "External optimizer",
    "external_optimizer_yes_text" : "",

    "additional_software" : "Additional software required",
    "gui" : "GUI",

    "citation_reference" : "Citation references",
    "citation_DOI" : "Citation doi",
    "references_to_reports_produced_using_the_model" : "Report references",
    "larger_scale_usage" : "",

    # Framework
    "model_types_grid" : "",
    "model_types_demand_simulation": "",
    "model_types_feed_in_simulation": "",
    "model_types_other": "",
    "model_types_other_text": "",

    "api_doc": "",
    "data_api": "",
    "abstraction": "",
    "used": ""
    }

EM_Map = {
    "model_name" : "Full Model Name",
    "acronym" : "",
    "institutions" : "Author institution",
    "authors" : "Authors",
    "current_contact_person" : "Contact Persons",
    "contact_email" : "Contact Email",
    "website" : "Website",
    "logo" : "Logo",
    "primary_purpose" : "Primary purpose",
    "primary_outputs" : "Primary outpurs",
    "support" : "Support",

    "framework" : "",
    "framework_yes_text" : "",

    "user_documentation" : "User documentation",
    "code_documentation" : "Code documentation",
    "documentation_quality" : "",
    "source_of_funding" : "Source of funcing",
    "open_source" : "Open source licensed",
    "open_up" : "Open future",
    "costs" : "",
    "license" : "License",
    "license_other_text" : "",
    "source_code_available" : "Model source public",
    "gitHub" : "",
    "link_to_source_code" : "Link to source",
    "data_provided" : "Data availability",
    "cooperative_programming" : "",
    "number_of_devolopers" : "Number of developers",
    "number_of_users" : "Number of users",
    "modelling_software" : "Modelling software",
    "interal_data_processing_software" : "Processing software",

    "external_optimizer" : "External optimizer",
    "external_optimizer_yes_text" : "",

    "additional_software" : "Additional software required",
    "gui" : "GUI",

    "citation_reference" : "Citation references",
    "citation_DOI" : "Citation doi",
    "references_to_reports_produced_using_the_model" : "Report references",
    "larger_scale_usage" : "",

    # Energymodel

    "energy_sectors": "Sectors",

    "demand_sectors" : "",

    "energy_carrier_gas": "Energy carrier (Gas)",

    "energy_carrier_liquid": "Energy carrier (Liquid)",

    "energy_carrier_solid": "Energy carrier (Solid)",

    "energy_carrier_renewables": "Energy carrier (Renewable)",

    "generation": "Technologies",

    "transfer_electricity" : "Transfer (Electricity)",

    "transfer_gas" : "Transfer (Gas)",

    "transfer_heat" : "Transfer (Heat)",

    "network_coverage" : "Network coverage",


    "storage_electricity": "Storage (Electricity)",

    "storage_heat" : "Storage (Heat)",
    "storage_gas" : "Storage (Gas)",

    "user_behaviour" : "User Behaviour",
    "user_behaviour_yes_text" : "",
    "changes_in_efficiency" : "Changes in Efficiency",

    "market_models" : "Market model",

    "geographical_coverage" : "Georegions",

    "georesolution" : "Georesolution",


    "comment_on_geo_resolution" : "",
    "timeresolution": "Timeresolution",

    "observation_period": "Observation period",

    "time_resolution_other" : "",
    "time_resolution_other_text" : "",


    "additional_dimensions_sector_ecological" : "Additional dimensions (Ecological)",
    "additional_dimensions_sector_economical" : "Additional dimensions (Economical)",
    "additional_dimensions_sector_social" : "Additional dimensions (Social)",
    "additional_dimensions_sector_others" : "Additional dimensions (Others)",

    "model_class": "Model class",


    "short_description_of_mathematical_model_class" : "Math modeltype shortdesc",
    "math_objective": "Math objective",

    "deterministic": "Deterministic",

    "montecarlo" : "Montecarlo",

    "typical_computation_time" : "Computation time minutes",

    "typical_computation_hardware" : "Computation Hardware",
    "technical_data_anchored_in_the_model" : "",

    "example_research_questions" : "Example research questions",

    "validation": "Validation",
    "validation_others_text" : "Description on Validation",

    "model_specific_properties" : "Specific properties",

    "interfaces" : "Interfaces",
    "model_file_format" : "Model file format",
    "model_input" : "Model input file format",
    "model_output" : "Model output file format",
    "integrating_models" : "Integrating models",
    "integrated_models" : "Integrated models",

# Missing: decisions, model_class, number_of_variables, computation_time_comments
    }

ST_MAP = {
    "name_of_the_study": "Name of the stud",
    "author_Institution": "Authors",
    "client": "Clients",

    "funding_private": "Funding",
    "funding_public": "",
    "funding_no_funding": "",

    "citation_reference": "Citation references",
    "citation_doi": "Citation doi",
    "aim": "Aim",
    "new_aspects": "New aspects",
    "spatial_Geographical_coverage": "",

    "time_frame": "Time frame",
    "time_frame_2020": "",
    "time_frame_2030": "",
    "time_frame_2050": "",
    "time_frame_other": "",
    "time_frame_other_text": "",

    "target_year": "Target year",
    "transformation_path": "Transformation path",
    "time_frame_2_target_year": "",
    "time_frame_2_transformation_path": "",

    "tools_models": "Used models",
    "tools_tools": "Used tools",

    "modeled_energy_sectors": "Modelled energy sectors",
    "modeled_energy_sectors_electricity": "",
    "modeled_energy_sectors_heat": "",
    "modeled_energy_sectors_liquid_fuels": "",
    "modeled_energy_sectors_gas": "",
    "modeled_energy_sectors_others": "",
    "modeled_energy_sectors_others_text": "",

    "modeled_demand_sectors": "Modelled demand sectors",
    "modeled_demand_sectors_households": "",
    "modeled_demand_sectors_industry": "",
    "modeled_demand_sectors_commercial_sector": "",
    "modeled_demand_sectors_transport": "",

    "economic_behavioral": "Economic behavioral",
    "economic_behavioral_perfect": "",
    "economic_behavioral_myopic": "",
    "economic_behavioral_qualitative": "",
    "economic_behavioral_agentbased": "",
    "economic_behavioral_other": "",
    "economic_behavioral_other_text": "",

    "renewables": "Renewables",
    "renewables_PV": "",
    "renewables_wind": "",
    "renewables_hydro": "",
    "renewables_biomass": "",
    "renewables_biogas": "",
    "renewables_solar": "",
    "renewables_others": "",
    "renewables_others_text": "",

    "conventional_generation": "Conventional",
    "conventional_generation_gas": "",
    "conventional_generation_coal": "",
    "conventional_generation_oil": "",
    "conventional_generation_liquid": "",
    "conventional_generation_nuclear": "",

    "CHP": "CHP",

    "networks": "Networks",
    "networks_electricity_gas_electricity": "",
    "networks_electricity_gas_gas": "",
    "networks_electricity_gas_heat": "",


    "storages_battery": "",
    "storages_kinetic": "",
    "storages_CAES": "",
    "storages_PHS": "",
    "storages_chemical": "",

    "economic_focuses_included": "Economic focuses",
    "social_focuses_included": "Social focuses",
    "endogenous_variables": "Endogenous variables",
    "sensitivities": "Sensitivities",

    "time_steps": "Time steps",
    "time_steps_anual": "",
    "time_steps_hour": "",
    "time_steps_15_min": "",
    "time_steps_1_min": "",
    "time_steps_sec": "",
    "time_steps_other": "",
    "time_steps_other_text": ""
}

SC_MAP ={
    "study": "Study",

    "exogenous_time_series_used": "Exogenous time series used",
    "exogenous_time_series_used_climate": "",
    "exogenous_time_series_used_feedin": "",
    "exogenous_time_series_used_loadcurves": "",
    "exogenous_time_series_used_others": "",
    "exogenous_time_series_used_others_text": "",

    "technical_data": "Technical data",
    "social_data": "Social data",
    "economical_data": "Economical data",
    "ecological_data": "Ecological data",
    "preProcessing": "Preprocessing",
    "name_of_scenario": "Full model name",

    "energy_saving_amount": "Energy saving",
    "energy_saving_kind": "Energy saving kind",
    "energy_saving_year": "Energy saving year",
    "potential_energy_savings_amount": "Potential energy saving",
    "potential_energy_savings_kind": "Potential energy saving kind",
    "potential_energy_savings_year": "Potential energy saving year",
    "emission_reductions_amount": "Emission reductions",
    "emission_reductions_kind": "Emission reductions kind",
    "emission_reductions_year": "Emission reductions year",
    "share_RE_power_amount": "Share RE (Power)",
    "share_RE_power_kind": "Share RE (Power) kind",
    "share_RE_power_year": "Share RE (Power) year",
    "share_RE_heat_amount": "Share RE (Heat)",
    "share_RE_heat_kind": "Share RE (Heat) kind",
    "share_RE_heat_year": "Share RE (Heat) year",
    "share_RE_mobility_amount": "Share RE (Mobility)",
    "share_RE_mobility_kind": "Share RE (Mobility) kind",
    "share_RE_mobility_year": "Share RE (Mobility) year",
    "share_RE_total_amount": "Share RE (Total)",
    "share_RE_total_kind": "Share RE (Total) kind",
    "share_RE_total_year": "Share RE (Total) year",

    "cost_development": "Cost development",
    "cost_development_capex": "",
    "cost_development_opex": "",
    "cost_development_learning_curves": "",
    "cost_development_constant": "",
    "cost_development_rediscount": "",

    "technological_innovations": "Technological innovations",

    "potential_wind": "Potential (Wind)",
    "potential_wind_whole": "",
    "potential_wind_technical": "",
    "potential_wind_economical": "",
    "potential_wind_ecological": "",
    "potential_wind_other": "",
    "potential_wind_other_text": "",

    "potential_solar_electric": "Potential (Solar)",
    "potential_solar_electric_whole": "",
    "potential_solar_electric_technical": "",
    "potential_solar_electric_economical": "",
    "potential_solar_electric_ecological": "",
    "potential_solar_electric_other": "",
    "potential_solar_electric_other_text": "",

    "potential_solar_thermal": "Potential (Thermal)",
    "potential_solar_thermal_whole": "",
    "potential_solar_thermal_technical": "",
    "potential_solar_thermal_economical": "",
    "potential_solar_thermal_ecological": "",
    "potential_solar_thermal_other": "",
    "potential_solar_thermal_other_text": "",

    "potential_biomass": "Potential (Biomass)",
    "potential_biomass_whole": "",
    "potential_biomass_technical": "",
    "potential_biomass_economical": "",
    "potential_biomass_ecological": "",
    "potential_biomass_other": "",
    "potential_biomass_other_text": "",

    "potential_geothermal": "Potential (Geothermal)",
    "potential_geothermal_whole": "",
    "potential_geothermal_technical": "",
    "potential_geothermal_economical": "",
    "potential_geothermal_ecological": "",
    "potential_geothermal_other": "",
    "potential_geothermal_othertext": "",

    "potential_hydro": "Potential (Hydro)",
    "potential_hydro_power_whole": "",
    "potential_hydro_power_technical": "",
    "potential_hydro_power_economical": "",
    "potential_hydro_power_ecological": "",
    "potential_hydro_power_other": "",
    "potential_hydro_power_other_text": "",

    "social_developement": "Social development",
    "economic_development": "Economic development",
    "development_of_environmental_aspects": "Development of enviromental aspects",
    "postprocessing": "Postprocessing",
    "further_assumptions_for_postprocessing": "Assumptions for postprocessing",
    "further_assumptions_for_postprocessing_text": "",
    "uncertainty_assessment": "Uncertainity assessment",
    "robustness": "Robustness",
    "comparability_Validation": "Comparability validation",
    "conclusions": "Conclusions"
}


def load_EM(name):
    properties = set(EM_Map.values())
    prop_query = "|?".join(properties)
    query = 'http://wiki.openmod-initiative.org/api.php?format=json&action=ask&query=[[Category:Model]]%s'%(prop_query)
    print(query)
    result = requests.get(query).json()
    type_map = {p['label']:p['typeid'] for p in result['query']['printrequests']}
    result = result['query']['results'][name]['printouts']
    m = Energymodel()

    for key in EM_Map:
        x = {'label': EM_Map[key]}
        if EM_Map[key] in result:
            x['value'] = result[EM_Map[key]]
            x['type'] = type_map[EM_Map[key]]
        else:
            x['value'] = None
            x['type'] = None
        print(x)
        setattr(m, key, x)

    m.pagetitle = name
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
