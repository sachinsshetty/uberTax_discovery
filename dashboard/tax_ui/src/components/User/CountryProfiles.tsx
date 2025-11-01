// File: CountryProfiles.tsx (updated - fetch from backend)
import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Typography, TextField, CircularProgress, Box } from '@mui/material';
import { CountryProfileData } from './CountryProfileData';  // ES module import

interface CountryProfilesProps {
  onSelectCountry: (country: CountryProfileData) => void;
}

const API_URL = import.meta.env.VITE_DWANI_API_BASE_URL || 'http://localhost:8000';

const columns: any[] = []; // Not used, keeping Table for simplicity

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
      return Object.keys(obj).reduce((result, key) => {
        result[camelize(key)] = camelizeKeys(obj[key]);
        return result;
      }, {});
    }
    return obj;
  };

  // Fetch country profiles from backend
  const fetchCountryProfiles = async () => {
    try {
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
      setError(`Failed to load country profiles: ${err.message}`);
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
    try {
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

      const data = await response.json();
      console.log('Query response:', data);

      setNaturalResponse(data.natural_response || '');

      if (data.results && Array.isArray(data.results)) {
        const camelized = camelizeKeys(data.results);
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
  };

  const displayData = filteredData.length > 0 ? filteredData : data;
  const hasSearchResults = searchResults.length > 0;
  const showTable = !hasSearchResults && (displayData.length > 0 || searchLoading || loading);

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
            Search Results:
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
          <TableContainer sx={{ '& .MuiTableCell-root': { color: 'grey.300' } }}>
            <Table>
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
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {!showTable && !hasSearchResults && displayData.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'grey.500' }}>
          <Typography>No data available.</Typography>
        </Box>
      )}
    </>
  );
};

export default CountryProfiles;