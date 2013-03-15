/*
 * SUMMARY:      flowgen.h -- header file for FlowGen.c
 * USAGE:        
 *
 * AUTHOR:       Bart Nijssen
 * ORG:          University of Washington, Department of Civil Engineering
 * E-MAIL:       nijssen@u.washington.edu
 * ORIG-DATE:    17-Apr-97 at 09:26:22
 * Last Changed:     Tue Nov 10 17:35:50 1998 by Bernt Viggo Matheussen
 * DESCRIPTION:  
 * DESCRIP-END.
 * FUNCTIONS:    
 * COMMENTS:     
 */

 /* $Id$ */

#ifndef FLOWGEN_H
#define FLOWGEN_H

#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE !TRUE
#endif
#ifndef BUFSIZE
#define BUFSIZE 255
#endif

#define DEF_FRACTION 0.4        /* default fraction */
#define INVALID -1

#define SINK -9
#define OUTLET 9

typedef unsigned char BOOLEAN;

typedef struct {
  int StartCol;
  int StartRow;
  int **FlowDirection;
} CORNER_INFO;

typedef struct node *NODEPTR;

typedef struct node {
  long Acc;
  NODEPTR Next;
  int FlowDirection;
} CORNER_NODE;

const char *Usage = 
"<accumulation file> <number of rows> <number of columns>\n       <output file> <number of rows per cell> <number of columns per cell>\n       [-m mask file] [-f fraction] [-o outside basin value] [-verbose]\n\nFor more details see readme\n\n";

int FindFlowDirection(long **Matrix, int NRows, int NCols, long *Border, 
		      int *FlowDirection, int CornerRows, int MiddleRows, 
		      int CornerCols, int MiddleCols, 
		      CORNER_NODE **CornerMatrix, CORNER_INFO *Corner, 
		      long MaxAccumulation);

void InitFlowDirections(int NRows, int NCols, float Fraction, 
                        long **Border, int **FlowDirection, 
                        int *CornerRows, int *MiddleRows, int *CornerCols, 
                        int *MiddleCols, CORNER_INFO *Corner, 
                        CORNER_NODE ***CornerMatrix);

int TrackFlow(NODEPTR Start, CORNER_NODE **CornerMatrix, int NRows, int NCols);


#endif
