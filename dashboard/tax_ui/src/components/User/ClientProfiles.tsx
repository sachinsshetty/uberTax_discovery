import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Box from '@mui/material/Box';
import { Button, Typography, TextField, CircularProgress } from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridToolbarContainer,
  useGridApiContext,
} from '@mui/x-data-grid';
import { fetchClientProfiles } from '../../redux/reducer/user/ClientProfilesReducer';
import { RootState, AppDispatch } from '../../redux/store';

const API_URL = import.meta.env.VITE_DWANI_API_BASE_URL || 'http://localhost:8000';

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
  const originalData = clients || [];
  const [filteredData, setFilteredData] = React.useState<ClientProfile[]>([]);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [searchLoading, setSearchLoading] = React.useState(false);
  const [naturalResponse, setNaturalResponse] = React.useState('');
  const effectiveLoading = reduxLoading || originalData.length === 0;
  const effectiveError = reduxError;

  React.useEffect(() => {
    // Optional: Dispatch if no prop data, but prefer prop to match UserApp
    if (originalData.length === 0) {
      dispatch(fetchClientProfiles());
    }
  }, [dispatch, originalData.length]);

  const camelizeKeys = (obj: any): any => {
    const camelize = (str: string): string => str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    
    if (Array.isArray(obj)) {
      return obj.map(camelizeKeys);
    } else if (obj !== null && typeof obj === 'object') {
      return Object.keys(obj).reduce((result, key) => {
        result[camelize(key)] = camelizeKeys(obj[key]);
        return result;
      }, {});
    }
    return obj;
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setNaturalResponse('');
    try {
      const url = `${API_URL}/api/clients/natural-query`;
      console.log('Querying natural language search:', url, searchQuery);
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_query: searchQuery }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Query HTTP ${response.status}: ${response.statusText} - Body: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Query response:', data);

      setNaturalResponse(data.natural_response || '');

      if (data.raw_data && Array.isArray(data.raw_data)) {
        const camelized = camelizeKeys(data.raw_data);
        setFilteredData(camelized);
      } else {
        // Fallback to original data if no raw_data
        setFilteredData(originalData);
      }
    } catch (error) {
      console.error('Error querying clients:', error);
      // Optionally set an error state
      setFilteredData(originalData);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleClear = () => {
    setFilteredData([]);
    setNaturalResponse('');
    setSearchQuery('');
  };

  const displayData = filteredData.length > 0 ? filteredData : originalData;

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

      {/* Search Bar */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'end' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask a question about clients, e.g., Show me all clients from Croatia"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          disabled={searchLoading}
          sx={{ '& .MuiOutlinedInput-root': { backgroundColor: '#1e2d4a' } }}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={searchLoading || !searchQuery.trim()}
          sx={{ minWidth: 100 }}
        >
          {searchLoading ? <CircularProgress size={20} color="inherit" /> : 'Query'}
        </Button>
        {filteredData.length > 0 && (
          <Button
            variant="outlined"
            onClick={handleClear}
            disabled={searchLoading}
            sx={{ minWidth: 80, color: '#a8b2d1', borderColor: '#1e2d4a' }}
          >
            Clear
          </Button>
        )}
      </Box>

      {/* Natural Response */}
      {naturalResponse && (
        <Box
          sx={{
            mb: 2,
            p: 2,
            backgroundColor: '#1e2d4a',
            border: '1px solid #2a3b5a',
            borderRadius: 1,
          }}
        >
          <Typography sx={{ whiteSpace: 'pre-line', color: 'grey.300', fontSize: '0.875rem' }}>
            {naturalResponse}
          </Typography>
        </Box>
      )}

      <DataGrid
        rows={displayData}
        columns={columns}
        getRowId={(row) => row.clientId}
        slots={{
          toolbar: CustomToolbar,
        }}
        loading={effectiveLoading || searchLoading}
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