// File: CountryProfileData.ts (updated - remove static data, keep interface)
export interface CountryProfileData {
  country: string;
  mandateStatus: string;
  archivingPeriod: string;
  scope: {
    triggers: {
      residents: string;
      nonResidentsWithVatId: string;
      logic: string;
    };
    b2b: {
      status: string;
      startDate: string;
      posRelevant: string;
      staggered: {
        applies: string;
        threshold: string;
      };
    };
    b2g: {
      status: string;
      startDate: string;
      staggered: {
        applies: string;
        threshold: string;
      };
    };
    b2c: {
      reportingObligation: string;
      startDate: string;
    };
    buyersChoice: {
      applies: string;
      condition: string;
    };
  };
  architecture: {
    model: {
      type: string;
      cornerModel: string;
      description: string;
    };
    formats: {
      en16931: {
        status: string;
        version: string;
      };
      nationalCius: {
        applies: string;
        schemaName: string;
      };
      allowedSyntaxes: string[];
      pdfConform: string;
    };
    transmission: {
      peppol: {
        status: string;
      };
    };
  };
  reporting: {
    statePlatform: {
      applies: string;
      name: string;
      mandatory: string;
    };
    clearance: {
      realTimeCtc: string;
      validityAfterRelease: string;
    };
    reportingReq: {
      drr: string;
      realTime: string;
      frequency: string;
    };
  };
  additional: {
    systemCert: string;
    saft: {
      obligation: string;
      submission: string;
    };
    localIds: {
      obligation: string;
      type: string;
    };
    transactionStatusReporting: string;
    specialNotes: string;
    sanctions: string;
  };
}
