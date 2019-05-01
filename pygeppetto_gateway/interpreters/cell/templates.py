MODEL = '''<?xml version="1.0" encoding="ASCII"?>
    <gep:GeppettoModel xmi:version="2.0"
            xmlns:xmi="http://www.omg.org/XMI"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:gep="https://raw.githubusercontent.com/openworm/org.geppetto.model/master/src/main/resources/geppettoModel.ecore"
            xmlns:gep_1="https://raw.githubusercontent.com/openworm/org.geppetto.model/master/src/main/resources/geppettoModel.ecore#//types"
            xmlns:gep_2="https://raw.githubusercontent.com/openworm/org.geppetto.model/master/src/main/resources/geppettoModel.ecore#//values"
        >
    <variables
        id="{target}"
        name=""
        types="//@libraries.0/@types.0"/>
    <libraries
        id="neuroml"
        name="NeuroML">
        <types xsi:type="gep_1:ImportType"
            id="{target}"
            url="{url}"
            modelInterpreterId="neuroMLModelInterpreter" />
    </libraries>
</gep:GeppettoModel>'''

PROJECT = '''{{
    "id":1,
    "name":"{project_name}",
    "activeExperimentId":1,
    "experiments":[
        {{
            "id":1,
            "name":"{project_name}Experiment",
            "status":"DESIGN",
            "aspectConfigurations":[
                {{
                "id":1,
                "instance":"{target}",
                "simulatorConfiguration":{{
                        "id":1,
                        "simulatorId":"scidashSimulator",
                        "conversionServiceId": "lemsConversion",
                        "timestep":0.000025,
                        "length":0.800025,
                        "parameters": {{
                            "target": "{target}",
                            "scoreID": "{score_id}"
                        }}
                    }},
                    "watchedVariables": {watched_variables}
                }}
            ]
        }}
    ],
    "geppettoModel":{{
        "id":1,
        "url":"{url}",
        "type":"GEPPETTO_PROJECT"
    }}
}}'''

