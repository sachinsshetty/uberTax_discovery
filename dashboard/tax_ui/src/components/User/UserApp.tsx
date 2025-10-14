import { Component } from 'react';
import { Container, Grid, Typography } from '@mui/material';
import ClientProfiles from './ClientProfiles';

type UserAppProps = {
};

class UserApp extends Component<UserAppProps> {

  render() {
    return (
      <div>
        <Container>
          <Typography variant="h4" gutterBottom>
            Client Profiles
          </Typography>
        </Container>
        <Container>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <ClientProfiles />
            </Grid>
          </Grid>
        </Container>
      </div>
    );
  }
}

export default UserApp;