import os
import glob
import re
import sys
import shutil
import argparse
import shutil

# example cmd:
# python clean_map.py input/compartments/ output/ --model-version 1.0.2
# python clean_map.py input/subsystems/ output/ --model-version 1.0.2 --skip-rm-compartment

parser = argparse.ArgumentParser(description='Short sample app')

parser.add_argument('input_dir', action="store")
parser.add_argument('output_dir', action="store")
parser.add_argument('model_name', action="store", )
parser.add_argument('model_version', action="store")
parser.add_argument('--skip-svgo', action="store_true", default=False, dest="skip_svgo")
parser.add_argument('--skip-rm-compartment', action="store_true", default=False, dest="skip_rm_compartment")
parser.add_argument('--skip-add-license', action="store_true", default=False, dest="skip_license")


results = parser.parse_args()
input_dir = results.input_dir
output_dir = results.output_dir
skip_svgo = results.skip_svgo
skip_rm_compartment = results.skip_rm_compartment
skip_license = results.skip_license
model_name = results.model_name
model_version = results.model_version


input_dir = os.path.abspath(input_dir)
output_dir = os.path.abspath(output_dir)

os.chdir(input_dir)
if not os.path.isdir(output_dir):
  os.makedirs(output_dir)

# this function remove all the compartment box and text in the svg files
# must run on the compartment maps only, compartment boxes in the subsystem maps must remain
def remove_compartment(input_dir, output_dir):
  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)
  os.chdir(input_dir)
  for f in glob.glob("*.svg"):
    output_file = os.path.join(output_dir, f)
    output_file = os.path.abspath(output_file)
    if f == "mitochondria.svg":
      shutil.copyfile(f, output_file)
      continue
    with open(f) as fh, open(output_file, 'w') as fw:
      write = True
      for line in fh:
        if 'class="compartment"' in line:
          write = False
        elif 'class="subsystem"' in line:
          write = True
        if write:
          fw.write(line)

def add_license_and_metadata(input_dir, output_dir):
  license_meta = '''  <metadata>
    <rdf:RDF xmlns:rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:cc = "http://creativecommons.org/ns#"
      xmlns:dc = "http://purl.org/dc/elements/1.1/">
      <rdf:Description about="license"
           dc:description="Copyright Department of Biology and Biological Engineering, Chalmers University of Technology. This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. Obtained from https://metabolicatlas.org"
           cc:license="http://creativecommons.org/licenses/by-sa/4.0/">
      </rdf:Description>
      <cc:License rdf:about="http://creativecommons.org/licenses/by-sa/4.0/">
        <cc:permits rdf:resource="http://creativecommons.org/ns#Reproduction" />
        <cc:permits rdf:resource="http://creativecommons.org/ns#Distribution" />
        <cc:requires rdf:resource="http://creativecommons.org/ns#Notice" />
        <cc:requires rdf:resource="http://creativecommons.org/ns#Attribution" />
        <cc:permits rdf:resource="http://creativecommons.org/ns#DerivativeWorks" />
        <cc:requires rdf:resource="http://creativecommons.org/ns#ShareAlike" />
      </cc:License>
    </rdf:RDF>
  </metadata>
  '''

  license_logos = '''<g id="license" transform="matrix(2,0,0,2,XXXX,YYYY)">
    <g>
      <path d="M3.408.476l113.354.202c1.584 0 3-.235 3 3.16l-.14 37.33H.547V3.7C.547 2.026.71.476 3.407.476z" fill="#aab2ab"/>
      <g transform="matrix(1,0,0,1,-177.69409,-74.436409) matrix(0.872921,0,0,0.872921,50.12536,143.2144)">
        <path id="path5906_2_" d="M187.21-55.68c.005 8.681-7.028 15.722-15.709 15.728-8.68.005-15.722-7.028-15.727-15.708v-.02c-.005-8.68 7.028-15.721 15.708-15.726 8.682-.006 15.722 7.028 15.727 15.708v.019z" fill="#fff"/>
        <g id="g5706_2_" transform="translate(-289.6157,99.0653)">
          <path id="path5708_2_" d="M473.885-167.547c3.485 3.486 5.228 7.754 5.228 12.802 0 5.05-1.713 9.272-5.138 12.668-3.636 3.576-7.932 5.364-12.89 5.364-4.898 0-9.12-1.772-12.665-5.32-3.546-3.545-5.318-7.782-5.318-12.712 0-4.928 1.772-9.195 5.318-12.802 3.455-3.487 7.677-5.23 12.665-5.23 5.048 0 9.314 1.743 12.8 5.23zm-23.118 2.345c-2.947 2.976-4.42 6.463-4.42 10.462 0 3.998 1.458 7.455 4.374 10.37 2.917 2.917 6.389 4.375 10.417 4.375 4.029 0 7.53-1.472 10.507-4.419 2.826-2.735 4.24-6.177 4.24-10.326 0-4.118-1.437-7.613-4.308-10.485-2.871-2.87-6.35-4.306-10.439-4.306-4.088 0-7.546 1.443-10.371 4.329zm7.754 8.703c-.45-.982-1.124-1.472-2.023-1.472-1.59 0-2.384 1.069-2.384 3.208 0 2.14.795 3.21 2.384 3.21 1.05 0 1.799-.522 2.248-1.566l2.203 1.173c-1.05 1.865-2.625 2.799-4.725 2.799-1.62 0-2.918-.497-3.892-1.49-.976-.993-1.463-2.362-1.463-4.107 0-1.716.502-3.078 1.507-4.086 1.006-1.008 2.257-1.513 3.758-1.513 2.22 0 3.81.875 4.771 2.623l-2.384 1.22zm10.363 0c-.45-.982-1.111-1.472-1.982-1.472-1.621 0-2.432 1.069-2.432 3.208 0 2.14.81 3.21 2.432 3.21 1.051 0 1.787-.522 2.207-1.566l2.252 1.173c-1.048 1.865-2.62 2.799-4.717 2.799-1.618 0-2.913-.497-3.887-1.49-.972-.993-1.46-2.362-1.46-4.107 0-1.716.495-3.078 1.484-4.086.987-1.008 2.245-1.513 3.773-1.513 2.216 0 3.804.875 4.761 2.623l-2.43 1.22z"/>
        </g>
      </g>
      <path d="M117.753 0H2.247A2.25 2.25 0 0 0 0 2.247v39.245c0 .28.227.508.507.508h118.985c.28 0 .508-.228.508-.508V2.247A2.25 2.25 0 0 0 117.753 0zM2.247 1.015h115.506c.68 0 1.232.553 1.232 1.232v27.245H36.428c-3.026 5.47-8.856 9.185-15.546 9.185-6.694 0-12.522-3.711-15.547-9.185h-4.32V2.247c0-.68.552-1.232 1.232-1.232z"/>
      <g fill="#fff">
        <path d="M86.264 37.732c.08.155.186.28.32.376.132.096.287.167.466.213.18.047.365.07.556.07.13 0 .268-.01.416-.032.148-.022.287-.064.417-.126a.9.9 0 0 0 .323-.255.635.635 0 0 0 .13-.413.581.581 0 0 0-.172-.435 1.355 1.355 0 0 0-.45-.279 4.54 4.54 0 0 0-.628-.194 16.854 16.854 0 0 1-.713-.186 6.254 6.254 0 0 1-.723-.227 2.486 2.486 0 0 1-.63-.348 1.637 1.637 0 0 1-.45-.533 1.63 1.63 0 0 1-.17-.775c0-.34.072-.635.217-.886.146-.25.336-.459.57-.626.235-.167.5-.29.797-.371.296-.08.593-.12.89-.12.346 0 .678.038.996.116.317.077.6.203.847.376.248.173.444.394.59.664.144.269.217.595.217.979h-1.413a1.192 1.192 0 0 0-.124-.492.826.826 0 0 0-.282-.306 1.197 1.197 0 0 0-.402-.158 2.455 2.455 0 0 0-.494-.046 1.72 1.72 0 0 0-.35.037.943.943 0 0 0-.318.13.796.796 0 0 0-.236.232.63.63 0 0 0-.092.352c0 .13.024.236.073.316.05.08.148.155.293.222a3.7 3.7 0 0 0 .601.205c.256.068.591.154 1.006.26.123.024.294.07.513.134.22.065.437.169.653.31.217.143.403.334.561.571.157.239.236.543.236.914 0 .304-.06.585-.177.845-.117.26-.292.484-.524.672-.232.19-.519.336-.861.441a4.078 4.078 0 0 1-1.192.158c-.365 0-.72-.045-1.063-.135a2.675 2.675 0 0 1-.91-.423 2.107 2.107 0 0 1-.625-.734c-.155-.298-.228-.65-.222-1.058h1.413c0 .222.04.411.12.565zM94.47 32.747l2.477 6.622h-1.513l-.5-1.475h-2.478l-.52 1.475h-1.465l2.505-6.622h1.493zm.083 4.06l-.835-2.427H93.7l-.864 2.428h1.717z"/>
      </g>
      <g fill="#fff">
        <path d="M59.997 32.747c.315 0 .603.029.863.084.26.056.484.147.67.274.185.126.33.295.432.505.102.21.153.47.153.778 0 .334-.076.612-.228.834-.151.223-.376.405-.673.547.41.118.715.323.917.617.202.294.303.649.303 1.063 0 .334-.066.623-.196.867a1.7 1.7 0 0 1-.525.599c-.22.154-.471.269-.753.343a3.381 3.381 0 0 1-.87.111h-3.215v-6.622h3.122zm-.187 2.679c.26 0 .474-.062.642-.185.167-.124.25-.324.25-.601a.77.77 0 0 0-.083-.38.62.62 0 0 0-.224-.231.945.945 0 0 0-.32-.116 2.12 2.12 0 0 0-.376-.032h-1.365v1.545h1.476zm.086 2.81c.142 0 .278-.014.408-.042.13-.027.246-.074.345-.139a.707.707 0 0 0 .237-.264.903.903 0 0 0 .088-.426c0-.34-.096-.583-.288-.728-.193-.145-.447-.218-.762-.218h-1.59v1.817h1.562zM62.69 32.747h1.634l1.55 2.616 1.542-2.616h1.624l-2.459 4.08v2.542h-1.46v-2.578l-2.43-4.044z"/>
      </g>
      <path d="M102.403 14.98c.004 5.846-4.731 10.588-10.577 10.592-5.846.005-10.588-4.73-10.593-10.576v-.015C81.229 9.135 85.965 4.394 91.81 4.389c5.846-.004 10.59 4.731 10.593 10.576v.016z" fill="#fff"/>
      <path d="M91.742 3.386c-3.212 0-5.93 1.12-8.156 3.362-2.283 2.32-3.425 5.064-3.425 8.233 0 3.169 1.142 5.894 3.425 8.174 2.283 2.28 5.002 3.42 8.156 3.42 3.193 0 5.96-1.15 8.303-3.449 2.205-2.183 3.308-4.899 3.308-8.145 0-3.246-1.123-5.991-3.367-8.233-2.245-2.241-4.993-3.362-8.244-3.362zm.03 2.087c2.631 0 4.866.927 6.705 2.783 1.857 1.836 2.786 4.077 2.786 6.725 0 2.666-.909 4.88-2.728 6.638-1.916 1.894-4.17 2.84-6.764 2.84-2.593 0-4.828-.937-6.705-2.81-1.877-1.876-2.815-4.098-2.815-6.668 0-2.57.948-4.812 2.844-6.725 1.82-1.856 4.044-2.783 6.676-2.783z"/>
      <path d="M86.603 13.344c.462-2.917 2.516-4.477 5.09-4.477 3.702 0 5.958 2.686 5.958 6.268 0 3.495-2.4 6.21-6.016 6.21-2.488 0-4.714-1.53-5.12-4.534h2.921c.088 1.56 1.1 2.108 2.546 2.108 1.648 0 2.72-1.53 2.72-3.87 0-2.455-.927-3.755-2.663-3.755-1.272 0-2.37.462-2.603 2.05l.85-.004-2.3 2.299-2.299-2.3.916.005z"/>
      <g transform="matrix(1,0,0,1,-177.69409,-74.436409)">
        <circle cx="242.562" cy="90.225" r="10.806" fill="#fff"/>
        <path d="M245.69 87.098a.754.754 0 0 0-.754-.754h-4.772a.754.754 0 0 0-.754.754v4.773h1.33v5.652h3.618V91.87h1.332v-4.773z"/>
        <circle cx="242.55" cy="84.083" r="1.632"/>
        <path clip-rule="evenodd" d="M242.535 78.318c-3.232 0-5.969 1.128-8.208 3.384-2.298 2.333-3.446 5.095-3.446 8.284 0 3.19 1.148 5.932 3.446 8.227s5.034 3.442 8.208 3.442c3.213 0 5.998-1.156 8.353-3.471 2.22-2.197 3.33-4.93 3.33-8.198 0-3.267-1.129-6.028-3.387-8.284-2.26-2.256-5.025-3.384-8.296-3.384zm.029 2.1c2.648 0 4.897.934 6.747 2.8 1.87 1.848 2.805 4.104 2.805 6.768 0 2.684-.915 4.911-2.746 6.681-1.928 1.906-4.197 2.858-6.806 2.858-2.61 0-4.858-.942-6.747-2.83-1.89-1.885-2.833-4.122-2.833-6.709 0-2.586.954-4.842 2.862-6.767 1.83-1.867 4.07-2.801 6.718-2.801z" fill-rule="evenodd"/>
      </g>
    </g>
    <text font-family="Arial" font-size="32" font-style="italic" stroke="#FFF" stroke-width=".5" transform="matrix(1,0,0,1,128,29)">
      metabolicAtlas.org
    </text>
  </g>'''

  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)
  os.chdir(input_dir)
  for f in glob.glob("*.svg"):
    output_file = os.path.join(output_dir, f)
    output_file = os.path.abspath(output_file)

    # add metadata and license
    with open(f) as fh, open(output_file, 'w') as fw:
      for i, line in enumerate(fh):
        if i == 1:
          # get the width and heigth, pos and scale
          width = line.split('width="')[1].split('"')[0]
          height = line.split('height="')[1].split('"')[0]
          posX = float(width) - 800
          posY = float(height) - 88
          if model_name:
            line =line.replace('data-pluginversion', 'data-modelname="%s" data-pluginversion' % model_name)
          if model_version:
            line =line.replace('data-pluginversion', 'data-modelversion="%s" data-pluginversion' % model_version)
        elif i == 2:
          fw.write(license_meta)
        elif line.strip() == "</g></svg>" or line.strip() == "</svg>":
          ll = license_logos.replace('XXXX', str(posX))
          ll = ll.replace('YYYY', str(posY))
          if line.strip() == "</g></svg>":
            fw.write("  </g>\n  " + ll)
          else:
            fw.write(ll)
          line = "\n</svg>"
        fw.write(line)


# optimize the input svg files with SVGO software
def run_svgo(input_dir, output_dir):
  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)
  os.chdir(input_dir)
  for f in glob.glob("*.svg"):
    print ("Reading (svgo)", f)
    output_file = os.path.join(output_dir, f)
    output_file = os.path.abspath(output_file)
    f = "'" + f + "'"
    output_file = "'" + output_file + "'"
    # os.system('svgo --disable=cleanupIDs --disable=convertTransform --disable=convertPathData --indent=2 --pretty -i %s -o %s' % (f, output_file))
    os.system('svgo --disable=cleanupIDs --disable=convertTransform --indent=2 --pretty -i %s -o %s' % (f, output_file))


if __name__ == "__main__":
  output_dir = os.path.abspath(output_dir)
  step1_dir = os.path.join(output_dir, "STEP1")
  step2_dir = os.path.join(output_dir, "STEP2")
  final_dir = os.path.join(output_dir, "FINAL")

  if not os.path.isdir(step1_dir):
    os.makedirs(step1_dir)

  if not skip_rm_compartment:
    remove_compartment(input_dir, step1_dir)
  else:
    step1_dir = input_dir

  if not os.path.isdir(step2_dir):
    os.makedirs(step2_dir)

  if not skip_license:
    add_license_and_metadata(step1_dir, step2_dir)
  else:
    step2_dir = step1_dir

  if not os.path.isdir(final_dir):
    os.makedirs(final_dir)

  if not skip_svgo:
    run_svgo(step2_dir, final_dir)
