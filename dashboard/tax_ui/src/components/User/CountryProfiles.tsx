import React, { useState, useEffect, useMemo } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Typography, TextField, CircularProgress, Box } from '@mui/material';
import { CountryProfileData } from './CountryProfileData';  // ES module import

// FIXED: Helper to ensure HTTPS for API URLs (fallback to localhost for dev)
const getApiBaseUrl = (): string => {
  let baseUrl = import.meta.env.VITE_DWANI_API_BASE_URL || 'http://localhost:8000';
  // Force HTTPS in production (detect via window.location)
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    baseUrl = baseUrl.replace(/^http:/, 'https:');
    if (baseUrl.includes('localhost')) {
      baseUrl = 'https://localhost:8000'; // Adjust port if needed; use self-signed cert for local HTTPS
    }
  }
  return baseUrl;
};

const API_URL = getApiBaseUrl();  // FIXED: Use HTTPS-safe URL

interface CountryProfilesProps {
  onSelectCountry: (country: CountryProfileData) => void;
}

// FIXED: Removed unused 'columns' declaration

const CountryProfiles: React.FC<CountryProfilesProps> = ({ onSelectCountry }) => {
  const [data, setData] = useState<CountryProfileData[]>([]);
  const [filteredData, setFilteredData] = useState<CountryProfileData[]>([]);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [naturalResponse, setNaturalResponse] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const camelizeKeys = (obj: any): any => {
    const camelize = (str: string): string => str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    
    if (Array.isArray(obj)) {
      return obj.map(camelizeKeys);
    } else if (obj !== null && typeof obj === 'object') {
      // FIXED: Type the accumulator and initial value to include an index signature
      return Object.keys(obj).reduce((result: Record<string, any>, key: string) => {
        result[camelize(key)] = camelizeKeys(obj[key]);
        return result;
      }, {} as Record<string, any>);
    }
    return obj;
  };

  // Fetch country profiles from backend
  const fetchCountryProfiles = async () => {
    try {
      // FIXED: Use HTTPS-safe API_URL
      const url = `${API_URL}/api/countries/profiles`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const rawData = await response.json();
      const camelized = camelizeKeys(rawData);
      setData(camelized);
      setFilteredData(camelized);
      setError(null);
    } catch (err) {
      console.error('Error fetching country profiles:', err);
      // FIXED: Type guard 'err' as Error to safely access .message
      setError(`Failed to load country profiles: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCountryProfiles();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setNaturalResponse('');
    setFilteredData([]);
    setSearchResults([]);
    setError(null); // NEW: Clear previous errors
    try {
      // FIXED: Use HTTPS-safe API_URL
      const url = `${API_URL}/api/clients/natural-query`;
      console.log('Querying natural language search:', url, searchQuery);
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_query: searchQuery, table_name: "country_profiles" }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Query HTTP ${response.status}: ${response.statusText} - Body: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      console.log('Query response:', responseData);

      setNaturalResponse(responseData.natural_response || '');

      if (responseData.results && Array.isArray(responseData.results)) {
        const camelized = camelizeKeys(responseData.results);
        // Check if full profile data (has country)
        if (camelized.length > 0 && camelized[0].country) {
          setFilteredData(camelized as CountryProfileData[]);
        } else {
          // Partial data, e.g., only country, show as simple text list
          setSearchResults(camelized);
        }
      } else {
        // Fallback to fetched data if no results
        setFilteredData(data);
      }
    } catch (error) {
      console.error('Error querying countries:', error);
      setError(error instanceof Error ? error.message : 'An unexpected error occurred'); // NEW: Set user-friendly error
      // Optionally set an error state
      setFilteredData(data);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleClear = () => {
    setFilteredData(data);
    setSearchResults([]);
    setNaturalResponse('');
    setSearchQuery('');
    setError(null); // NEW: Clear errors on reset
  };

  // NEW: Sort display data by country name ascending for better UX (alphabetical)
  const displayData = useMemo(() => {
    const dataToSort = filteredData.length > 0 ? filteredData : data;
    return [...dataToSort].sort((a, b) => (a.country || '').localeCompare(b.country || ''));
  }, [filteredData, data]);

  const hasSearchResults = searchResults.length > 0;
  const showTable = !hasSearchResults && (displayData.length > 0 || searchLoading || loading);
  const shouldScrollTable = displayData.length > 10; // NEW: Conditional scrollbar

  // NEW: Table container styles with conditional maxHeight for scrollbar
  const tableContainerSx = useMemo(() => ({
    maxHeight: shouldScrollTable ? 400 : 'none',
    overflow: shouldScrollTable ? 'auto' : 'visible',
    '& .MuiTableCell-root': { color: 'grey.300' }
  }), [shouldScrollTable]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>Loading country profiles...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', py: 4, color: 'error.main' }}>
        <Typography>{error}</Typography>
        <Button variant="outlined" onClick={fetchCountryProfiles} sx={{ mt: 1 }}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <>
      {/* NEW: Component Header for better UX */}
      <Typography variant="h6" sx={{ mb: 2, color: 'grey.300', fontWeight: 600 }}>
        Country Profiles
        {displayData.length > 0 && (
          <Typography component="span" variant="body2" sx={{ ml: 1, color: 'grey.500' }}>
            ({displayData.length} countries)
          </Typography>
        )}
      </Typography>

      {/* Search Bar */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'end', flexWrap: 'wrap' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask a question about countries, e.g., Show me countries with B2B mandate"
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

      {/* NEW: Error Display for Search */}
      {error && !loading && (
        <Box
          sx={{
            mb: 2,
            p: 2,
            backgroundColor: '#3d2b1f',
            border: '1px solid #5d4037',
            borderRadius: 1,
            color: 'warning.main',
          }}
        >
          <Typography variant="body2">
            Error: {error}
          </Typography>
        </Box>
      )}

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

      {/* Simple Text Box Output for Partial Search Results */}
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
            Search Results ({searchResults.length}):
          </Typography>
          {searchResults.map((item, index) => (
            <Typography key={index} variant="body2" sx={{ color: 'grey.300', mb: 0.5 }}>
              {item.country || item.country_name || 'Unknown Country'}
            </Typography>
          ))}
        </Box>
      )}

      {/* Table for Full Profiles */}
      {showTable && (
        <Paper sx={{ mb: 3, backgroundColor: '#112240', border: '1px solid #1e2d4a' }}>
          <TableContainer sx={tableContainerSx}>
            {/* NEW: Sticky header for better UX when scrolling */}
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Country</TableCell>
                  <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Mandate Status</TableCell>
                  <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>B2B Start Date</TableCell>
                  <TableCell sx={{ color: 'grey.400', fontWeight: '600' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {displayData.map((country, index) => (
                  <TableRow key={index} hover sx={{ '&:hover': { backgroundColor: '#1e2d4a' } }}>
                    <TableCell sx={{ color: 'grey.300' }}>
                      <Typography variant="body2" fontWeight="500">{country.country}</Typography>
                    </TableCell>
                    <TableCell sx={{ color: 'grey.300' }}>
                      <Typography variant="body2">{country.mandateStatus}</Typography>
                    </TableCell>
                    <TableCell sx={{ color: 'grey.300' }}>
                      <Typography variant="body2">{country.scope?.b2b?.startDate || 'N/A'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => onSelectCountry(country)}
                        sx={{ color: '#64ffda', borderColor: '#64ffda', '&:hover': { borderColor: '#64ffda', bgcolor: 'rgba(100, 255, 218, 0.04)' } }}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {displayData.length === 0 && (searchLoading || loading) && (
                  <TableRow>
                    <TableCell colSpan={4} sx={{ textAlign: 'center', py: 4 }}>
                      <CircularProgress size={20} />
                      <Typography variant="body2" sx={{ mt: 1, color: 'grey.500' }}>
                        {searchLoading ? 'Searching...' : 'Loading...'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {!showTable && !hasSearchResults && displayData.length === 0 && !loading && !searchLoading && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'grey.500' }}>
          <Typography>No data available. Try searching for specific countries!</Typography>
        </Box>
      )}
    </>
  );
};

export default CountryProfiles;