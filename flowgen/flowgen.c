/*
 * SUMMARY:      FlowGen.c - program to generate flow networks
 * USAGE:        FlowGen 
 *
 * AUTHOR:       Bart Nijssen
 * ORG:          University of Washington, Department of Civil Engineering
 * E-MAIL:       nijssen@u.washington.edu
 * ORIG-DATE:    16-Apr-97 at 17:42:38
 * Last Changed: Tue Aug 25 15:11:06 1998 by Bart Nijssen <nijssen@u.washington.edu>
 * DESCRIPTION:  Generate flow network from an accumulation flow
 * DESCRIP-END.
 * FUNCTIONS:    
 * COMMENTS:     
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "flowgen.h"

BOOLEAN Verbose = FALSE;        /* flag for optional verbose */
char FlowChar[] = {' ', '|', '/', '-', '\\', '|', '/', '-', '\\'};
/*char FlowChar[] = {' ', '1', '2', '3', '4', '5', '6', '7', '8'};*/

int main(int argc, char **argv)
{
  BOOLEAN HasFraction = FALSE;  /* flag for whether fraction is provided */
  BOOLEAN HasMask = FALSE;      /* flag for optional mask */
  BOOLEAN HasUserDefOutsideValue = FALSE;
				/* flag whether a user defined value is given
				   to indicate values outside the basin */
  BOOLEAN **MaskMatrix;         /* matrix with mask */
  char AccFilename[BUFSIZE+1];  /* filename for accumulation file */
  char MaskFilename[BUFSIZE+1]; /* filename for mask file */
  char OutFilename[BUFSIZE+1];  /* filename for output file */
  char *EndPtr = NULL;
  FILE *AccFile = NULL;         /* accumulation file */
  FILE *MaskFile = NULL;        /* optional mask file */
  FILE *OutFile = NULL;         /* output  */
  float Fraction;               /* fraction of border through which flow 
                                   exits perpendicular */
  int i;                        /* counter */
  int j;                        /* counter */
  int m;                        /* counter */
  int n;                        /* counter */
  int AccCols;                  /* number of columns in accumulation file */
  int AccRows;                  /* number of rows in accumulation file */
  int CellCols;                 /* number of columns per cell */
  int CellRows;                 /* number of rows per cell */
  int Col;
  int CornerCols;
  int CornerRows;
  int ExtraCols;                /* superfluous columns in accumulation file */
  int ExtraRows;                /* superfluous rows in accumulation file */
  int MiddleCols;
  int MiddleRows;
  int OutCols;                  /* number of columns in output file */
  int OutRows;                  /* number of rows in output file */
  int Row;
  int *FlowDirection;           /* array with flow directions */
  int **FlowMatrix;             /* matrix with flow directions */
  size_t NRead;			/* number of records read */
  long *Border;			/* cells on the border */
  long **AccMatrix;		/* matrix with accumulation totals */
  long **CellMatrix;		/* matrix with accumulation totals for a single 
				   cell */
  long **MaxAccMatrix;		/* matrix with maximum accumulation total */
  long OutletAccumulation;	/* largest accumulation value in 
				   AccMatrix */
  long UserDefOutsideValue;	/* User defined value indicating which values
				   are outside the basin */
  CORNER_INFO Corner[4];
  CORNER_NODE **CornerMatrix;
  
  /****************************************************************************/
  /* read the command-line options                                            */
  /****************************************************************************/
  
  /* Echo the function call to the screen */

  printf("\n\n");
  for (i = 0; i < argc; i++)
    printf("%s ", argv[i]);
  printf("\n\n");

  /* Get command-line options */

  if (argc < 7) {
    fprintf(stderr, "Usage: %s %s\n\n", argv[0], Usage);
    exit(EXIT_FAILURE);
  }

  /* Read information about accumulation file */

  strcpy(AccFilename, *++argv);
  --argc;
  AccRows = (int) strtol(*++argv, &EndPtr, 0);
  --argc;
  if ((EndPtr != NULL && EndPtr[0] != '\0') || AccRows < 0) {
    fprintf(stderr, "%s: Not a valid number of rows\n\n", *argv);
    exit(EXIT_FAILURE);      
  }
  AccCols = (int) strtol(*++argv, &EndPtr, 0);
  --argc;
  if ((EndPtr != NULL && EndPtr[0] != '\0') || AccCols < 0) {
    fprintf(stderr, "%s: Not a valid number of columns\n\n", *argv);
    exit(EXIT_FAILURE);      
  }

  /* Read information about output file */

  strcpy(OutFilename, *++argv);
  --argc;
  CellRows = (int) strtol(*++argv, &EndPtr, 0);
  --argc;
  if ((EndPtr != NULL && EndPtr[0] != '\0') || CellRows < 0) {
    fprintf(stderr, "%s: Not a valid number of rows\n\n", *argv);
    exit(EXIT_FAILURE);      
  }
  if (CellRows < 2) {
    fprintf(stderr, 
            "%s: Number of rows per cell must be at least 2\n",
            *argv);
    exit(EXIT_FAILURE);      
  }

  CellCols = (int) strtol(*++argv, &EndPtr, 0);
  --argc;
  if ((EndPtr != NULL && EndPtr[0] != '\0') || CellCols < 0) {
    fprintf(stderr, "%s: Not a valid number of columns\n\n", *argv);
    exit(EXIT_FAILURE);      
  }
  if (CellCols < 2) {
    fprintf(stderr, 
            "%s: Number of columns per cell must be at least 2\n",
            *argv);
    exit(EXIT_FAILURE);      
  }

  OutRows = AccRows/CellRows;
  ExtraRows = AccRows % CellRows;
  if (ExtraRows != 0) {
    fprintf(stderr, 
            "Warning: The number of output rows is not an integer\n");
    fprintf(stderr,
            "multiple of the number of rows in the accumulation file.\n");
    fprintf(stderr, 
            "The last %d rows in the accumulation file will not be \n", 
            ExtraRows);
    fprintf(stderr, 
            "taken into account\n\n");
    AccRows -= ExtraRows;
  }
  OutCols = AccCols/CellCols;
  ExtraCols = AccCols % CellCols;
  if (ExtraCols != 0) {
    fprintf(stderr, 
            "Warning: The number of output columns is not an integer\n");
    fprintf(stderr,
            "multiple of the number of columns in the accumulation file.\n");
    fprintf(stderr, 
            "The last %d columns in the accumulation file will not be \n", 
            ExtraCols);
    fprintf(stderr, 
            "taken into account\n\n");
    AccCols -= ExtraCols;
  }
    
  /* Read the remaining options */

  while (argc-- > 1 && (*++argv)[0] == '-') {
    switch (*++argv[0]) {
    case 'f':
      if (argc > 1) {
        HasFraction = TRUE;
        Fraction = (float) strtod(*++argv, &EndPtr);
        if ((EndPtr != NULL && EndPtr[0] != '\0') || 
            Fraction < 0 || Fraction > 1) {
          fprintf(stderr, "%s: Fraction has to be between 0 and 1\n\n", *argv);
          exit(EXIT_FAILURE);      
        }
        --argc;
      }
      else {
        fprintf(stderr, 
                "-f flag needs to be followed by a number between 0 and 1\n");
        exit(EXIT_FAILURE);
      }
      break;
    case 'm':
      if (argc > 1) {
        HasMask = TRUE;
        strcpy(MaskFilename, *++argv);
        --argc;
      }
      else {
        fprintf(stderr, "-m flag needs to be followed by a valid filename\n");
        exit(EXIT_FAILURE);
      }
      break;
    case 'o':
      if (argc > 1) {
        HasUserDefOutsideValue = TRUE;
	UserDefOutsideValue = (long) strtol(*++argv, &EndPtr, 0);
        if (EndPtr != NULL && EndPtr[0] != '\0') {
          fprintf(stderr, "%s: Outside basin value has to be an integer value", 
		  *argv);
	  exit(EXIT_FAILURE);      
	}
	--argc;
      }
      else {
        fprintf(stderr, 
                "-o flag needs to be followed by a number\n");
        exit(EXIT_FAILURE);
      }
      break;
    case 'v':
      Verbose = TRUE;
      break;
    default:
      fprintf(stderr, "Unrecognized option: %s\n\n", *argv);
      fprintf(stderr, "Usage: %s %s\n\n", argv[0], Usage);
      exit(EXIT_FAILURE);
      break;
    }
  }

  if (HasFraction == FALSE) {
    Fraction = DEF_FRACTION;
    if (Verbose)
      printf("Default fraction used: %.3f\n", Fraction);
  }

  /****************************************************************************/
  /* Allocate memory                                                          */
  /****************************************************************************/

  AccMatrix = (long **) calloc(AccRows, sizeof(long *));
  if (AccMatrix == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < AccRows; i++) {
    AccMatrix[i] = (long *) calloc(AccCols, sizeof(long));
    if (AccMatrix == NULL) {
      perror(NULL);
      exit(EXIT_FAILURE);
    }
  }

  MaskMatrix = (BOOLEAN **) calloc(AccRows, sizeof(BOOLEAN *));
  if (MaskMatrix == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < AccRows; i++) {
    MaskMatrix[i] = (BOOLEAN *) calloc(AccCols, sizeof(BOOLEAN));
    if (MaskMatrix == NULL) {
      perror(NULL);
      exit(EXIT_FAILURE);
    }
  }

  FlowMatrix = (int **) calloc(OutRows, sizeof(int *));
  if (FlowMatrix == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < OutRows; i++) {
    FlowMatrix[i] = (int *) calloc(OutCols, sizeof(int));
    if (FlowMatrix == NULL) {
      perror(NULL);
      exit(EXIT_FAILURE);
    }
  }

  MaxAccMatrix = (long **) calloc(OutRows, sizeof(long *));
  if (MaxAccMatrix == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < OutRows; i++) {
    MaxAccMatrix[i] = (long *) calloc(OutCols, sizeof(long));
    if (MaxAccMatrix == NULL) {
      perror(NULL);
      exit(EXIT_FAILURE);
    }
  }

  /****************************************************************************/
  /* Open and read files                                                      */
  /****************************************************************************/

  AccFile = fopen(AccFilename, "rb");
  if (AccFile == NULL) {
    perror(AccFilename);
    exit(EXIT_FAILURE);
  }
  if (Verbose)
    printf("%s opened for reading\n", AccFilename);
  
  for (i = 0; i < AccRows; i++) {
    NRead = fread(AccMatrix[i], sizeof(long), AccCols+ExtraCols, AccFile);
    if (NRead != AccCols + ExtraCols) {
      fprintf(stderr, "Row %d: %d columns read, %d columns expected\n\n", i,
              NRead, AccCols + ExtraCols);
      exit(EXIT_FAILURE);
    }
  }
  fclose(AccFile);

  if (HasUserDefOutsideValue) {
    for (i = 0; i < AccRows; i++) {
      for (j = 0; j < AccRows; j++) {
	if (AccMatrix[i][j] == UserDefOutsideValue || 
	    AccMatrix[i][j] < 0)
	  AccMatrix[i][j] = INVALID;
      }
    }
  }
  
  if (HasMask) {
    MaskFile = fopen(MaskFilename, "r");
    if (MaskFile == NULL) {
      perror(MaskFilename);
      exit(EXIT_FAILURE);
    }
    if (Verbose)
      printf("%s opened for reading\n", MaskFilename);

    for (i = 0; i < AccRows; i++) {
      NRead = fread(MaskMatrix[i], sizeof(BOOLEAN), AccCols+ExtraCols, 
		    MaskFile);
      if (NRead != AccCols + ExtraCols) {
        fprintf(stderr, "Row %d: %d columns read, %d columns expected\n\n", i,
                NRead, AccCols + ExtraCols);
        exit(EXIT_FAILURE);
      }
      fclose(MaskFile);
    }
  }
  else {
    for (i = 0; i < AccRows; i++) {
      for (j = 0; j < AccCols; j++) {
        MaskMatrix[i][j] = TRUE;
      }
    }
  }
  
  /****************************************************************************/
  /* Apply mask to accumulation file                                          */
  /****************************************************************************/

  for (i = 0; i < AccRows; i++) {
    for (j = 0; j < AccCols; j++) {
      if (MaskMatrix[i][j] == FALSE) {
        AccMatrix[i][j] = INVALID;
      }
    }
  }

  /****************************************************************************/
  /* Initialize the FlowMatrix, by putting a 1 in those cells that have at    */
  /* accumulation value not equal to INVALID                                  */
  /****************************************************************************/

  for (i = 0; i < OutRows; i++) {
    for (j = 0; j < OutCols; j++) {
      FlowMatrix[i][j] = INVALID;
      for (m = 0; m < CellRows; m++) {
	for (n = 0; n < CellCols; n++) {
	  if (AccMatrix[i*CellRows+m][j*CellCols+n] != INVALID) {
	    FlowMatrix[i][j] = 1;
	    break;
	  }
	}
	if (FlowMatrix[i][j] != INVALID)
	  break;
      }
    }
  }

  /****************************************************************************/
  /* Make a sweep to determine the maximum accumulation in each cell.  This   */
  /* will be used to determine which cells act as sinks.  This will clarify   */
  /* most of the problems with cells pointing to one another.                 */
  /****************************************************************************/

  OutletAccumulation = 0;
  for (i = 0; i < OutRows; i++) {
    for (j = 0; j < OutCols; j++) {
      MaxAccMatrix[i][j] = 0;
      if (FlowMatrix[i][j] != INVALID) {
	for (m = 0; m < CellRows; m++) {
	  for (n = 0; n < CellCols; n++) {
	    if (AccMatrix[i*CellRows+m][j*CellCols+n] != INVALID &&
		AccMatrix[i*CellRows+m][j*CellCols+n] > MaxAccMatrix[i][j]) {
	      MaxAccMatrix[i][j] = AccMatrix[i*CellRows+m][j*CellCols+n];
	    }
	  }
	}
	if (MaxAccMatrix[i][j] > OutletAccumulation)
	  OutletAccumulation = MaxAccMatrix[i][j];
      }
    }
  }
  
  /****************************************************************************/
  /* Initialize flow direction routines                                       */
  /****************************************************************************/

  if (Verbose)
    printf("Initializing flow directions ... \n");

  InitFlowDirections(CellRows, CellCols, Fraction, &Border, &FlowDirection,
                     &CornerRows, &MiddleRows, &CornerCols, &MiddleCols, 
                     Corner, &CornerMatrix);

  CellMatrix = (long **) calloc(CellRows+2*(CornerRows+1), sizeof(long *));
  if (CellMatrix == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < CellRows+2*(CornerCols+1); i++) {
    CellMatrix[i] = (long *) calloc(CellCols+2*(CornerCols+1), sizeof(long));
    if (CellMatrix == NULL) {
      perror(NULL);
      exit(EXIT_FAILURE);
    }
  }

  /****************************************************************************/
  /* Determine flow direction for every cell                                  */
  /****************************************************************************/

  if (Verbose)
    printf("Generating network ... \n");

  for (i = 0; i < OutRows; i++) {
    for (j = 0; j < OutCols; j++) {
      if (FlowMatrix[i][j] != INVALID) {
	
	/* Copy the appropriate values from the large AccMatrix to the small
	   CellMatrix */
	
	for (m = 0; m < CellRows + 2 * (CornerRows + 1); m++) {
	  for (n = 0; n < CellCols + 2 * (CornerCols + 1); n++) {
	    Row = m + i * CellRows - (CornerRows + 1);
	    Col = n + j * CellCols - (CornerCols + 1);
	    if (Row >= 0 && Row < AccRows && Col >= 0 && Col < AccCols)
	      CellMatrix[m][n] = AccMatrix[Row][Col];
	    else
	      CellMatrix[m][n] = INVALID;
	  }
	}
	
	/* Find the flow direction for the current cell */
	
	FlowMatrix[i][j] = FindFlowDirection(CellMatrix, CellRows, CellCols,
					     Border, FlowDirection, CornerRows,
					     MiddleRows, CornerCols, MiddleCols,
					     CornerMatrix, Corner, 
					     MaxAccMatrix[i][j]);

	if (FlowMatrix[i][j] == INVALID) {
	  fprintf(stderr, "We have a winner!!!!  Another feature!\n\n");
	  fprintf(stderr, "Invalid flow direction in row %d, column %d\n",
		  i, j);
	  /*         exit(EXIT_FAILURE); */
	}
	else if (FlowMatrix[i][j] == SINK) {
	  if (MaxAccMatrix[i][j] == OutletAccumulation)
	    FlowMatrix[i][j] = OUTLET;
	}
      }
    }
  }

  /****************************************************************************/
  /* Write the flow directions to the file                                    */
  /****************************************************************************/
  
  OutFile = fopen(OutFilename, "w");
  if (OutFile == NULL) {
    perror(OutFilename);
    exit(EXIT_FAILURE);
  }
  if (Verbose)
    printf("%s opened for writing\n", OutFilename);
  
  for (i = 0; i < OutRows; i++) {
    for (j = 0; j < OutCols; j++) {
      fprintf(OutFile, "%2d ", FlowMatrix[i][j]);
      if (Verbose) 
        printf("%2c", FlowChar[FlowMatrix[i][j]]);
    }
    fprintf(OutFile, "\n");
    if (Verbose) 
      printf("\n");
  }
  fclose(OutFile);
  
  if (Verbose) 
    printf("flowgen successfully completed\n");

  return EXIT_SUCCESS;
}

/******************************************************************************/
/* InitFlowDirection()                                                        */
/******************************************************************************/
void InitFlowDirections(int NRows, int NCols, float Fraction, 
                        long **Border, int **FlowDirection, 
                        int *CornerRows, int *MiddleRows, int *CornerCols, 
                        int *MiddleCols, CORNER_INFO *Corner, 
                        CORNER_NODE ***CornerMatrix)
{
  int i;                        /* counter */
  int j;                        /* counter */
  int m;                        /* counter */
  int BorderLength;             /* Length of border */

  BorderLength = 2 * (NRows + NCols) - 4;

  /* Allocate memory */
  *Border = (long *) calloc(BorderLength, sizeof(long));
  if (*Border == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }
  *FlowDirection = (int *) calloc(BorderLength, sizeof(int));
  if (*FlowDirection == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }

  *MiddleRows = Fraction * NRows;
  *CornerRows = NRows - *MiddleRows;
  if (*CornerRows % 2 != 0) {
    if (*CornerRows/(1-Fraction) > NRows) {
      (*CornerRows)--;
      (*MiddleRows)++;
    }
    else if (*MiddleRows > 0) {
      (*MiddleRows)--;
      (*CornerRows)++;
    }
    else {
      fprintf(stderr, "Cannot generate a proper direction matrix\n");
      exit(EXIT_FAILURE);
    }
  }
  *CornerRows /= 2;

  *MiddleCols = Fraction * NCols;
  *CornerCols = NCols - *MiddleCols;
  if (*CornerCols % 2 != 0) {
    if (*CornerCols/(1-Fraction) > NCols) {
      (*CornerCols)--;
      (*MiddleCols)++;
    }
    else if (*MiddleCols > 0) {
      (*MiddleCols)--;
      (*CornerCols)++;
    }
    else {
      fprintf(stderr, "Cannot generate a proper direction matrix\n");
      exit(EXIT_FAILURE);
    }
  }
  *CornerCols /= 2;

  m = 0;
  for (i = 0; i < *CornerCols; i++)
    (*FlowDirection)[m++] = 8;
  for (i = 0; i < *MiddleCols; i++)
    (*FlowDirection)[m++] = 1;
  for (i = 0; i < *CornerCols; i++)
    (*FlowDirection)[m++] = 2;
  for (i = 0; i < *CornerRows - 1; i++)
    (*FlowDirection)[m++] = 2;
  for (i = 0; i < *MiddleRows; i++)
    (*FlowDirection)[m++] = 3;
  for (i = 0; i < *CornerRows; i++)
    (*FlowDirection)[m++] = 4;
  for (i = 0; i < *CornerCols - 1; i++)
    (*FlowDirection)[m++] = 4;
  for (i = 0; i < *MiddleCols; i++)
    (*FlowDirection)[m++] = 5;
  for (i = 0; i < *CornerCols; i++)
    (*FlowDirection)[m++] = 6;
  for (i = 0; i < *CornerRows - 1; i++)
    (*FlowDirection)[m++] = 6;
  for (i = 0; i < *MiddleRows; i++)
    (*FlowDirection)[m++] = 7;
  for (i = 0; i < *CornerRows - 1; i++) 
    (*FlowDirection)[m++] = 8;

  if (Verbose) {
    printf("\nFlow direction grid:\n");
    for (i = 0; i < NCols; i++)
      printf("%1c ", FlowChar[(*FlowDirection)[i]]);
    printf("\n");
    for (i = 1; i < NRows - 1; i++) {
      printf("%1c ", FlowChar[(*FlowDirection)[BorderLength-i]]);
      for (j = 1; j < NCols - 1; j++)
        printf("  ");
      printf("%1c \n", FlowChar[(*FlowDirection)[NCols+i-1]]);
    }
    for (i = 0; i < NCols; i++)
      printf("%1c ", FlowChar[(*FlowDirection)[BorderLength-NRows+1-i]]);
    printf("\n\n");
  } 

  if (m != BorderLength) {
    fprintf(stderr, "Error in flow direction assignment\n");
    exit(EXIT_FAILURE);
  }

  /* Initialize the corner information */

  for (i = 0; i < 4; i++) {
    Corner[i].FlowDirection = (int **) calloc((2*(*CornerRows+1)), 
					      sizeof(int *));
    if (Corner[i].FlowDirection == NULL) {
      perror(NULL);
      exit(EXIT_FAILURE);
    }
    for (j = 0; j < 2 * (*CornerRows + 1); j++) {
      Corner[i].FlowDirection[j] = (int *) calloc((2*(*CornerCols+1)), 
                                                  sizeof(int));
      if (Corner[i].FlowDirection[j] == NULL) {
        perror(NULL);
        exit(EXIT_FAILURE);
      }
    }
  }

  /* Upper left, Index = 0 */

  Corner[0].StartRow = 0;
  Corner[0].StartCol = 0;
  for (i = 0; i < *CornerRows+1; i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[0].FlowDirection[i][j] = 8;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[0].FlowDirection[i][j] = 1;      
  }      
  for ( ; i < 2*(*CornerRows+1); i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[0].FlowDirection[i][j] = 7;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[0].FlowDirection[i][j] = INVALID;      
  }      

  /* Upper right, Index = 1 */

  Corner[1].StartRow = 0;
  Corner[1].StartCol = 2 * *CornerCols + *MiddleCols;
  for (i = 0; i < *CornerRows+1; i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[1].FlowDirection[i][j] = 1;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[1].FlowDirection[i][j] = 2;
  }      
  for ( ; i < 2*(*CornerRows+1); i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[1].FlowDirection[i][j] = INVALID;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[1].FlowDirection[i][j] = 3;
  }      
  
  /* Lower right, Index = 2 */

  Corner[2].StartRow = 2 * *CornerRows + *MiddleRows;
  Corner[2].StartCol = 2 * *CornerCols + *MiddleCols;
  for (i = 0; i < *CornerRows+1; i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[2].FlowDirection[i][j] = INVALID;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[2].FlowDirection[i][j] = 3;
  }      
  for ( ; i < 2*(*CornerRows+1); i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[2].FlowDirection[i][j] = 5;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[2].FlowDirection[i][j] = 4;
  }      
  
  /* Lower left, Index = 3 */

  Corner[3].StartRow = 2 * *CornerRows + *MiddleRows;
  Corner[3].StartCol = 0;
  for (i = 0; i < *CornerRows+1; i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[3].FlowDirection[i][j] = 7;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[3].FlowDirection[i][j] = INVALID;  
  }
  for ( ; i < 2*(*CornerRows+1); i++) {
    for (j = 0; j < *CornerCols+1; j++) 
      Corner[3].FlowDirection[i][j] = 6;
    for ( ; j < 2*(*CornerCols+1); j++)
      Corner[3].FlowDirection[i][j] = 5;
  }

  *CornerMatrix = 
    (CORNER_NODE **) calloc((2*(*CornerRows+1)), sizeof(CORNER_NODE *));
  if (*CornerMatrix == NULL) {
    perror(NULL);
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < (2*(*CornerRows+1)); i++) {
    (*CornerMatrix)[i] = 
      (CORNER_NODE *) calloc((2*(*CornerCols+1)), sizeof(CORNER_NODE));
    if ((*CornerMatrix)[i] == NULL) {
      perror(NULL);
      exit(EXIT_FAILURE);
    }
  }
}

/******************************************************************************/
/* FindFlowDirection()                                                        */
/******************************************************************************/

int FindFlowDirection(long **Matrix, int NRows, int NCols, long *Border, 
		      int *FlowDirection, int CornerRows, int MiddleRows, 
		      int CornerCols, int MiddleCols, 
		      CORNER_NODE **CornerMatrix, CORNER_INFO *Corner, 
		      long MaxAccumulation)
{
  int i;                        /* counter */
  int j;                        /* counter */
  int m;                        /* counter */
  int BorderLength;             /* Length of border */
  int Col;
  int Index;
  int MaxElement;               /* index of largest element in Border */
  int Row;
  long Max;			/* Maximum sum of accumulation in window */

  BorderLength = 2 * (NRows + NCols) - 4;
  
  /****************************************************************************/
  /* Store the accumulation totals on the edge of the Matrix in Border        */
  /****************************************************************************/
  
  /* last elements on edge */
  m = 0;

  /* Top edge */
  for (i = 0; i < NCols; i++)
    Border[m++] = Matrix[CornerRows+1][i+CornerCols+1];
  
  /* Right edge */
  for (i = 1; i < NRows; i++)
    Border[m++] = Matrix[i+CornerRows+1][CornerCols+1+NCols-1];

  /* Bottom edge */
  for (i = NCols - 2; i >= 0; i--)
    Border[m++] = Matrix[CornerRows+1+NRows-1][i+CornerCols+1];

  /* Left edge */
  for (i = NRows - 2; i > 0; i--)
    Border[m++] = Matrix[i+CornerRows+1][CornerCols+1];

  /****************************************************************************/
  /* Determine flow direction                                                 */
  /****************************************************************************/
  Max = 0;
  MaxElement = 0;
  for (i = 0; i < BorderLength; i++) {
    if (Border[i] != INVALID && Border[i] > Max) {
      Max = Border[i];
      MaxElement = i;
    }
  }
  
  if (Max == 0 && MaxElement == 0)
    return 0;
  else if (Border[MaxElement] < MaxAccumulation) 
    return SINK;
  else if (FlowDirection[MaxElement] % 2 == 1)
    return FlowDirection[MaxElement];
  else {

    /* MaxElement falls in a corner.  Track the flow path to see in which 
       direction the channel goes */

    Index = (FlowDirection[MaxElement] / 2) % 4;
    for (i = 0; i < 2 * (CornerRows + 1); i++) {
      for (j = 0; j < 2 * (CornerCols + 1); j++) {
        Row = i + Corner[Index].StartRow;
        Col = j + Corner[Index].StartCol;
        if (Matrix[Row][Col] != INVALID && Matrix[Row][Col] >= Max)
          CornerMatrix[i][j].Acc = Matrix[Row][Col];
        else
          CornerMatrix[i][j].Acc = INVALID;
        CornerMatrix[i][j].Next = NULL;
        CornerMatrix[i][j].FlowDirection = Corner[Index].FlowDirection[i][j];
      }
    }

    /* find the row and column of the largest element on the border */

    if (MaxElement < NCols) {
      Row = 0;
      Col = MaxElement;
    }
    else if (MaxElement < (NCols + NRows - 1)) {
      Row = MaxElement - (NCols - 1);
      Col = NCols - 1;
    }
    else if (MaxElement < (2 * NCols + NRows - 2)) {
      Row = NRows - 1;
      Col = NCols - 1 - (MaxElement - (NCols + NRows - 2));
    }
    else {
      Row = NRows - 1 - (MaxElement - (2 * NCols + NRows - 3));
      Col = 0;
    }

    Row += CornerRows+1;
    Col += CornerCols+1;
    Row -= Corner[Index].StartRow;
    Col -= Corner[Index].StartCol;

    return TrackFlow(&(CornerMatrix[Row][Col]), CornerMatrix, 
                       (2 * (CornerRows + 1)), (2 * (CornerCols + 1)));
  }
}

/******************************************************************************/
/* TrackFlow() - tracks the flow near a corner cell                           */
/******************************************************************************/

int TrackFlow(NODEPTR Start, CORNER_NODE **CornerMatrix, int NRows, int NCols)
{
  NODEPTR Trace;
  int i;
  int j;
  int m;
  int n;

  for (i = 0; i < NRows; i++) {
    for (j = 0; j < NCols; j++) {
      if (CornerMatrix[i][j].Acc != INVALID) {
        for (m = i-1; m <= i+1; m++) {
          for (n = j-1; n <= j+1; n++) {
            if (m >= 0 && m < NRows && n >= 0 && n < NCols) {
              if (CornerMatrix[m][n].Acc != INVALID &&
		  CornerMatrix[m][n].Acc > CornerMatrix[i][j].Acc) {
                if (CornerMatrix[i][j].Next == NULL)
                  CornerMatrix[i][j].Next = &(CornerMatrix[m][n]);
                else if (CornerMatrix[i][j].Next->Acc != INVALID &&
			 CornerMatrix[m][n].Acc > CornerMatrix[i][j].Next->Acc)
                  CornerMatrix[i][j].Next = &(CornerMatrix[m][n]);
              }
            }
          }
        }
      }
    }
  }

  Trace = Start;

  while (Trace->Next != NULL)
    Trace = Trace->Next;
                  
  if (Trace->FlowDirection == INVALID) 
    Trace->FlowDirection = SINK;

  return Trace->FlowDirection;
}
