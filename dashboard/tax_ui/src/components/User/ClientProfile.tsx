import React, {useState, useEffect} from 'react';
import Box from '@mui/material/Box';
import {Button, Typography} from '@mui/material';
import {DataGrid, GridColDef, GridToolbarContainer, useGridApiContext} from '@mui/x-data-grid';

interface ClientProfile {
  clientId: string;
  companyName: string;
  country: string;
  newRegulation: string;
  deadline: string | null;
  status: string;
}

const columns: GridColDef<ClientProfile>[] = [
  {field: 'clientId', headerName: 'Client ID', width: 150},
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
    valueFormatter: (params) => params.value || 'N/A',
  },
  {
    field: 'status',
    headerName: 'Status',
    width: 120,
    editable: false,
  },
];

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

function CustomToolbar() {
  return (
    <GridToolbarContainer>
      <CustomExportButton />
    </GridToolbarContainer>
  );
}

const ClientProfiles: React.FC = () => {
  const [rows, setRows] = useState<ClientProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/clients');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: ClientProfile[] = await response.json();
        setRows(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch clients');
      } finally {
        setLoading(false);
      }
    };

    fetchClients();
  }, []);

  if (error) {
    return (
      <Box sx={{height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{height: '100%', width: '100%'}}>
      <Typography variant="h6" gutterBottom sx={{mb: 2}}>
        Client Profiles
      </Typography>
      <DataGrid
        rows={rows}
        columns={columns}
        slots={{
          toolbar: CustomToolbar,
        }}
        loading={loading}
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
        }}
      />
    </Box>
  );
};

export default ClientProfiles;