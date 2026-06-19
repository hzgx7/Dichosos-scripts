#!/usr/bin/perl
#  Script que extrae la geometria y las energias scf
#  de un scan (solo puntos estacionarios).
#  NF-08-08-05 / fix indices y regex

@files=0;
$file=0;
$line=0;
$flag=0;$energy=0;
$x=0;$y=0;$z=0;$f=0;$n=0;$at=0;

@atoms=(Bq,H,He,Li,Be,B,C,N,O,F,Ne,Na,Mg,Al,Si,P,S,Cl,
Ar,K,Ca,Sc,Ti,V,Cr,Mn,
Fe,Co,Ni,Cu,Zn,Ga,Ge,As,Se,Br,Kr,Rb,Sr,Y,Zr,Nb,Mo,
Tc,Ru,Rh,Pd,Ag,Cd,In,Sn,Sb,
Te,I,Xe,Cs,Ba,La,Ce,Pr,Nd,Pm,Sm,Eu,Gd,Tb,Dy,Ho,Er,Tm,Yb,
Lu,Hf,Ta,W,Re,Os,Ir,Pt,Au,Hg,Tl,Pb,Bi,Po,At,Rn);

@files=@ARGV;

foreach $file (@files)
{
open (INP, "<$file") || die "I could not open $file\n";
open (OUT,"> $file.scan") || die "I could not open $file.scan\n";
$file=~s/\.com//i;
$file=~s/\.out//i;
$file=~s/\.log//i;
$file=~s/\.gjf//i;
$file=~s/\.xyz//i;
print "Reading $file\n";

while (<INP>)
   {
   $line=$_;

   if ($line=~m/SCF Done/)
      {
      $energy=(split( /\s+/, $line))[5];
      }

   if ($line=~m/Standard orientation:/ || $line=~m/Input orientation:/)
      {
      $flag=1;
      }

   if ($flag==1)
      {
      if($line=~m/^\s{2,}[0-9]{1,3}\s+([0-9]{1,2})\s+[0-9]{1}\s+([-0-9\.]+)\s+([-0-9\.]+)\s+([-0-9\.]+)/)
         {
         $n_atom[$n]=$1;
         $x[$n]=$2;
         $y[$n]=$3;
         $z[$n]=$4;
         $n++;
         $f=$n;
         }
      if($line=~m/Rotational/ || $line=~/Distance/)
         {
         $flag=0;
         $n=0;   # ← fix: era $n=1
         }
      }

   if ($line=~/Stationary point found/)
      {
      print "Writing stationary point\n";
      $at=$f;        # ← fix: era $f-1
      print(OUT "$at\n");
      print(OUT "scf done:  $energy\n");
      for ($j=0;$j<$f;$j++)   # ← fix: era j=1
         {
         write (OUT);
         }
      }
   }
}

format OUT =
@<<<<  @>>>>>>>>>  @>>>>>>>>>  @>>>>>>>>>
$atoms[$n_atom[$j]],$x[$j],$y[$j],$z[$j]
.
