import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Box from '@mui/material/Box';
import { Button, Typography } from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridToolbarContainer,
  useGridApiContext,
} from '@mui/x-data-grid';
import { fetchClientProfiles } from '../../redux/reducer/user/ClientProfilesReducer';
import { RootState, AppDispatch } from '../../redux/store';

interface ClientProfile {
  clientId: string;
  companyName: string;
  country: string;
  newRegulation: string;
  deadline: string | null;
  status: string;
}

interface ClientProfilesProps {
  clients: ClientProfile[];
}

const columns: GridColDef<ClientProfile>[] = [
  { field: 'clientId', headerName: 'Client ID', width: 150 },
  {
    field: 'companyName',
    headerName: 'Company Name',
    width: 250,
    editable: false,
  },
  {
    field: 'country',
    headerName: 'Country',
    width: 120,
    editable: false,
  },
  {
    field: 'newRegulation',
    headerName: 'New Regulation',
    width: 250,
    editable: false,
  },
  {
    field: 'deadline',
    headerName: 'Deadline',
    width: 120,
    editable: false,
    valueFormatter: (params) => params?.value ?? 'N/A',
  },
  {
    field: 'status',
    headerName: 'Status',
    width: 120,
    editable: false,
  },
];

/** render
 * @return {return}
 */
function CustomExportButton() {
  const apiRef = useGridApiContext();

  const handleExport = () => {
    apiRef.current.exportDataAsCsv({
      fileName: 'client-profiles',
    });
  };

  return (
    <Button onClick={handleExport} variant="outlined" size="small">
      Download CSV
    </Button>
  );
}

/** render
 * @return {return}
 */
function CustomToolbar() {
  return (
    <GridToolbarContainer>
      <CustomExportButton />
    </GridToolbarContainer>
  );
}

const ClientProfiles: React.FC<ClientProfilesProps> = ({ clients }) => {
  // Optional: Keep Redux for other features, but use props for data to avoid duplicate fetches
  const dispatch = useDispatch<AppDispatch>();
  const { loading: reduxLoading, error: reduxError } = useSelector(
    (state: RootState) => state.clientProfiles
  );

  // Use prop data primarily; fallback to Redux if needed
  const displayData = clients || [];
  const effectiveLoading = reduxLoading || displayData.length === 0;
  const effectiveError = reduxError;

  React.useEffect(() => {
    // Optional: Dispatch if no prop data, but prefer prop to match UserApp
    if (displayData.length === 0) {
      dispatch(fetchClientProfiles());
    }
  }, [dispatch, displayData.length]);

  if (effectiveError) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography color="error">{effectiveError}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', width: '100%' }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Client Profiles
      </Typography>
      <DataGrid
        rows={displayData}
        columns={columns}
        getRowId={(row) => row.clientId}
        slots={{
          toolbar: CustomToolbar,
        }}
        loading={effectiveLoading}
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 10,
              page: 0,
            },
          },
        }}
        pageSizeOptions={[5, 10, 25]}
        checkboxSelection
        disableRowSelectionOnClick
        sx={{
          '& .MuiDataGrid-cell': {
            fontSize: '0.875rem',
          },
          // Theme adjustments for dark mode consistency
          backgroundColor: '#112240',
          border: '1px solid #1e2d4a',
          color: 'grey.200',
          '& .MuiDataGrid-row:hover': {
            backgroundColor: '#1e2d4a',
          },
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: '#1e2d4a',
            color: 'grey.400',
          },
        }}
      />
    </Box>
  );
};

export default ClientProfiles;