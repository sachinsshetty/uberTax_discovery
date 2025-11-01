import React from 'react';
import Box from '@mui/material/Box';
import { Button, Typography, TextField, CircularProgress } from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridToolbarContainer,
  useGridApiContext,
} from '@mui/x-data-grid';

const getApiBaseUrl = (): string => {
  let baseUrl = import.meta.env.VITE_DWANI_API_BASE_URL || 'http://localhost:8000';
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    baseUrl = baseUrl.replace(/^http:/, 'https:');
    if (baseUrl.includes('localhost')) {
      baseUrl = 'https://localhost:8000';
    }
  }
  return baseUrl;
};

const API_URL = getApiBaseUrl();

interface ClientProfile {
  clientId: string;
  companyName: string;
  country: string;
  newRegulation: string;
  deadline: string | null;
  status: string;
}

interface SearchResult {
  companyName: string;
}

interface ClientProfilesProps {
  clients: ClientProfile[];
}

const columns: GridColDef<ClientProfile>[] = [
  { field: 'clientId', headerName: 'Client ID', flex: 0.8, minWidth: 120 },
  {
    field: 'companyName',
    headerName: 'Company Name',
    flex: 1.2,
    minWidth: 200,
    editable: false,
  },
  {
    field: 'country',
    headerName: 'Country',
    flex: 0.6,
    minWidth: 100,
    editable: false,
  },
  {
    field: 'newRegulation',
    headerName: 'New Regulation',
    flex: 1.5,
    minWidth: 200,
    editable: false,
  },
  {
    field: 'deadline',
    headerName: 'Deadline',
    flex: 0.6,
    minWidth: 100,
    editable: false,
    valueFormatter: (value) => value ?? 'N/A',
  },
  {
    field: 'status',
    headerName: 'Status',
    flex: 0.6,
    minWidth: 100,
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

const ClientProfiles: React.FC<ClientProfilesProps> = ({ clients }) => {
  const originalData = clients;
  const [filteredData, setFilteredData] = React.useState<ClientProfile[]>([]);
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([]);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [searchLoading, setSearchLoading] = React.useState(false);
  const [naturalResponse, setNaturalResponse] = React.useState('');

  const camelizeKeys = (obj: any): any => {
    const camelize = (str: string): string => str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    
    if (Array.isArray(obj)) {
      return obj.map(camelizeKeys);
    } else if (obj !== null && typeof obj === 'object') {
      return Object.keys(obj).reduce((result: Record<string, any>, key: string) => {
        result[camelize(key)] = camelizeKeys(obj[key]);
        return result;
      }, {} as Record<string, any>);
    }
    return obj;
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setNaturalResponse('');
    setFilteredData([]);
    setSearchResults([]);
    try {
      const url = `${API_URL}/api/clients/natural-query`;
      console.log('Querying natural language search:', url, searchQuery);
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_query: searchQuery, table_name: "client_profiles" }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Query HTTP ${response.status}: ${response.statusText} - Body: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Query response:', data);

      setNaturalResponse(data.natural_response || '');

      if (data.results && Array.isArray(data.results)) {
        const camelized = camelizeKeys(data.results);
        if (camelized.length > 0 && camelized[0].clientId) {
          setFilteredData(camelized as ClientProfile[]);
        } else {
          setSearchResults(camelized as SearchResult[]);
        }
      } else {
        setFilteredData(originalData);
      }
    } catch (error) {
      console.error('Error querying clients:', error);
      setFilteredData(originalData);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleClear = () => {
    setFilteredData([]);
    setSearchResults([]);
    setNaturalResponse('');
    setSearchQuery('');
  };

  const displayData = filteredData.length > 0 ? filteredData : originalData;
  const hasSearchResults = searchResults.length > 0;
  const showGrid = !hasSearchResults && (displayData.length > 0 || searchLoading);

  return (
    <Box sx={{ height: '100%', width: '100%' }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Client Profiles
      </Typography>

      <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'end', flexWrap: 'wrap' }}>
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
          sx={{ 
            '& .MuiOutlinedInput-root': { backgroundColor: '#1e2d4a' },
            flex: 1,
            minWidth: 300,
          }}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={searchLoading || !searchQuery.trim()}
          sx={{ minWidth: 100 }}
        >
          {searchLoading ? <CircularProgress size={20} color="inherit" /> : 'Query'}
        </Button>
        {(filteredData.length > 0 || hasSearchResults) && (
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

      {hasSearchResults && (
        <Box
          sx={{
            mb: 2,
            p: 2,
            backgroundColor: '#1e2d4a',
            border: '1px solid #2a3b5a',
            borderRadius: 1,
            maxHeight: 400,
            overflowY: 'auto',
          }}
        >
          <Typography variant="subtitle2" sx={{ mb: 1, color: 'grey.400' }}>
            Search Results:
          </Typography>
          {searchResults.map((item, index) => (
            <Typography key={index} variant="body2" sx={{ color: 'grey.300', mb: 0.5 }}>
              {item.companyName}
            </Typography>
          ))}
        </Box>
      )}

      {showGrid && (
        <DataGrid
          rows={displayData}
          columns={columns}
          getRowId={(row) => row.clientId}
          slots={{
            toolbar: CustomToolbar,
          }}
          loading={searchLoading}
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
            height: 500,
            '& .MuiDataGrid-cell': {
              fontSize: '0.875rem',
            },
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
            '& .MuiDataGrid-virtualScroller': {
              overflowX: 'auto',
            },
          }}
        />
      )}

      {!showGrid && !hasSearchResults && !searchLoading && displayData.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'grey.500' }}>
          <Typography>No data available.</Typography>
        </Box>
      )}
    </Box>
  );
};

export default ClientProfiles;