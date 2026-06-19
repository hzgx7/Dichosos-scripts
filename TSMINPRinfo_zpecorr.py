'''
This is a script written in python 3. It creates tables for publication purpose 
in LaTeX format. These tables contain information about the name and energies of 
MIN,TS and PR participating in those paths created by the AutoMeKin. It needs as
input the MINinfo, TSinfo and prod.db archos.

This script also provides new MIN, TS and PRODinfo documents with the ZPE energies corrected.

Marta Castiñeira Reis, l.v. 03/12/2023
'''

#Importing modules for a python 3 script
import os
import shutil
import numpy as np
import sqlite3

#------------------------------------------------------------------------------#
#                 Getting some relevant data from the user                     #
#------------------------------------------------------------------------------#

print("Can you please tell me who is your reference minimum?")
REFERENCE_MINIMUM = input()

print("Do you want to correct your ZPE, please porate the scaling factor. If your do not want to type 1.")
print("You can obtain your scaling factors from: J. Chem. Theory Comput. 2010, 6, 9, 2872-2887.")
scaling_factor = float(input())
#scaling_factor = float(0.972)

#stablishing references
PR121 = 0 
#PR121 = 363.35 
#PR121 = 310.6 
#PR14 = PR121
#------------------------------------------------------------------------------#
#                Definition of functions to create the tables                  #
#------------------------------------------------------------------------------#

def open_mins_edit_v3():
         '''
         This function creates a comprehensive LaTeX friendly table, that contains data of electronic energies,
         ZPVE energies, and relative energies of minima.
         '''
         content_db=[]
         cur=sqlite3.connect("min.db") #initiating a connection with the database
         #starting our table
         string = "\\begin{longtable}{|c| c| c| }\\hline"+os.linesep
         #header of the table
         string += " ID & Electronic Energy & ZVPE & Relative energies \\hline"+os.linesep
         #We iterate over the lines in the database to extract energies
         for row in cur.execute("select id,natom,name,lname,energy,zpe,g,geom,freq from min"):
             Eenergy = float(row[4])
             Eenergy_zpve = (float(row[4])+float(row[5])*0.00159362*scaling_factor)
             Rel_energy = (Eenergy_zpve - Eenergy_zpve_reference)*627.509

             string += "MIN"+str(row[0])+"    &    "+str(Eenergy)+"    &     "+str(Eenergy_zpve)+"    &    "+str(Rel_energy)+"\\\\\\hline"+os.linesep
         string += "\end{longtable}"+os.linesep
         # We write the desired information in a text file
         with open("MIN_energy_table",'w') as f: f.write(string)

def open_ts_edit_v3():
         '''
         This function creates a comprehensive LaTeX friendly table, that contains data of electronic energies,
         ZPVE energies, and relative energies of tss. The structure is the same as open_mins_edit_v3.
         '''
         content_db=[]
         cur=sqlite3.connect("ts.db") 
         string = "\\begin{longtable}{|c| c| c| }\\hline"+os.linesep
         string += " ID & Electronic Energy & ZVPE & Relative energies \\hline"+os.linesep
         for row in cur.execute("select id,natom,name,lname,energy,zpe,g,geom,freq from ts"):
             Eenergy = float(row[4])
             Eenergy_zpve = (float(row[4])+float(row[5])*0.00159362*scaling_factor)
             Rel_energy = (Eenergy_zpve - Eenergy_zpve_reference)*627.509
             string += "MIN"+str(row[0])+"    &    "+str(Eenergy)+"    &     "+str(Eenergy_zpve)+"    &    "+str(Rel_energy)+"\\\\\\hline"+os.linesep
         string += "\end{longtable}"+os.linesep

         with open("TS_energy_table",'w') as f: f.write(string)



def open_PR_edit_v2():
        content_db=[]
        #here we stablish a connection with the database that contains our data on the energies of the products.
        cur=sqlite3.connect("prod.db") #creamos conexion con la base de datos que queremos crear
        string = "\\begin{longtable}{|c| c| c|}\\hline"+os.linesep
        string += "ID & Electronic Energy & ZVPE & Relative energies \\hline"+os.linesep
        for row in cur.execute("select id,natom,name,energy,zpe,g,geom,freq,formula from prod"):
            #Last two numbers correspond to the E+ZPVE energy of bencene
            Eenergy = float(row[3])
            Eenergy_zpve = (float(row[3])+float(row[4])*0.00159362*scaling_factor) #HL
            Rel_energy = (float(Eenergy_zpve) - float(Eenergy_zpve_reference))
            string += "PR"+str(row[0])+"    &   "+str(Eenergy)+"   &   "+str(Eenergy_zpve)+"   &   "+str(Rel_energy)+"\\\\\\hline"+os.linesep
        string += "\end{longtable}"+os.linesep
        # escribir archivo
        with open("PR_energy_table",'w') as f: f.write(string)

def PRODinfo_creator():
    cur=sqlite3.connect("prod.db") #creamos conexion con la base de datos que queremos crear
    string = "PR #  DE(kcal/mol)"+'\n'
    string2 = "PR #  DE(kcal/mol)"+'\n'

    for row in cur.execute("select id,natom,name,energy,zpe,g,geom,freq,formula from prod"):
        Eenergy = float(row[3])
        Eenergy_zpve = (float(row[3])+float(row[4])*0.00159362)
        Eenergy_zpvecorr = (float(row[3])+float(row[4])*0.00159362*scaling_factor)
        #Rel_energy = (float(Eenergy_zpve) - float(Eenergy_zpve_reference))*627.509
        Rel_energy = (float(Eenergy_zpve) - float(Eenergy_zpve_reference))#*627.509 #LL
        Rel_energycorr = (float(Eenergy_zpvecorr) - float(Eenergy_zpve_referencecorr))*627.509 +PR121

        width = 3

        formatted_row = str(row[0]).rjust(width)+"      "+str(round(Rel_energy, 3))
        formatted_row2 = str(row[0]).rjust(width)+"      "+str(round(Rel_energycorr, 3))

        string += formatted_row + "\n"
        string2 += formatted_row2 + "\n"

        with open("PRODinfo", "w") as asdf:
            asdf.write(string)

        with open("PRODinfo_zpecorr", "w") as asdf:
            asdf.write(string2)


def MINinfo_creator():

    cur=sqlite3.connect("min.db") #creamos conexion con la base de datos que queremos crear
    string = "MIN #    DE(kcal/mol)"+'\n'
    string2 = string
    for row in cur.execute("select id,natom,name,lname,energy,zpe,g,geom,freq from min"):
        Eenergy = float(row[4])
        Eenergy_zpve = (float(row[4])+float(row[5])*0.00159362)
        Eenergy_zpvecorr = (float(row[4])+float(row[5])*0.00159362*scaling_factor)
        Rel_energy = (float(Eenergy_zpve) - float(Eenergy_zpve_reference))*627.509
        Rel_energycorr = (float(Eenergy_zpvecorr) - float(Eenergy_zpve_referencecorr))*627.509 +PR121


        width = 3

        formatted_row = str(row[0]).rjust(width)+"      "+str(round(Rel_energy, 3))
        formatted_row2 = str(row[0]).rjust(width)+"      "+str(round(Rel_energycorr, 3))

        string += formatted_row + "\n"
        string2 += formatted_row2 + "\n"


        with open("MINinfo_zpecorr", "w") as asdf:
            asdf.write(string2)


def TSinfo_creator():
    cur=sqlite3.connect("ts.db") #creamos conexion con la base de datos que queremos crear
    string = " TS  #    DE(kcal/mol)"+'\n'
    string2 = string
    for row in cur.execute("select id,natom,name,lname,energy,zpe,g,geom,freq from ts"):
        Eenergy = float(row[4])
        Eenergy_zpve = (float(row[4])+float(row[5])*0.00159362)
        Eenergy_zpvecorr = (float(row[4])+float(row[5])*0.00159362*scaling_factor)
        Rel_energy = (float(Eenergy_zpve) - float(Eenergy_zpve_reference))*627.509 
        Rel_energycorr = (float(Eenergy_zpvecorr) - float(Eenergy_zpve_referencecorr))*627.509 + PR121 

        width = 3

        formatted_row = str(row[0]).rjust(width)+"      "+str(round(Rel_energy, 3))
        formatted_row2 = str(row[0]).rjust(width)+"      "+str(round(Rel_energycorr, 3))
        formatted_row3 = str(row[0]).rjust(width)+"      "+str(round(Rel_energycorr, 3))

        string += formatted_row + "\n"
        string2 += formatted_row2 + "\n"


        with open("TSinfo_zpecorr", "w") as asdf:
            asdf.write(string2)


#-------------------------- HERE THE MAIN CODE STARTS -------------------------#
#1.  We identify our reference energy first: 
def finding_ref_E():
     cur=sqlite3.connect("min.db") 
     for row in cur.execute("select id,natom,name,lname,energy,zpe,g,geom,freq from min"):
         if "MIN"+str(row[0]) == REFERENCE_MINIMUM:
             Eenergy_zpve_reference = (float(row[4])+float(row[5])*0.00159362)

             Eenergy_zpve_referencecorr = (float(row[4])+float(row[5])*0.00159362*scaling_factor)

             break

     return Eenergy_zpve_reference,Eenergy_zpve_referencecorr

#2. We operate our functions to create the info archos with the Energies.
Eenergy_zpve_reference,Eenergy_zpve_referencecorr = finding_ref_E()
PRODinfo_creator()
MINinfo_creator()
TSinfo_creator()

#3. We operate our functions to create the SI-likely tables
#open_PR_edit_v2()
#open_ts_edit_v3()
#open_mins_edit_v3()




